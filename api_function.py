import json
import boto3
from boto3.dynamodb.conditions import Attr

IDENTIFIERS = [
    "MPN",
    "UPC",
    "EAN",
    "GTIN"
]

def get_unique_values(values):
    """
    Extracts unique values from a list of comma-separated values.

    Arguments:
        values {list} -- A list of strings containing comma-separated values.

    Returns:
        {list} -- A list of unique values extracted from the input list.
    """
    values_list = []
    for value in values:
        values_list += value.split(",")
    return list(set(values_list))

def check_identifiers_keys(parameters):
    """
    Checks for identifiers in the keys of a given parameters dictionary and returns unique identifier values.

    Arguments:
        parameters {dict} -- A dictionary containing parameter keys.

    Returns:
        {list} -- A list of unique identifier values found in the keys.
    """
    identifiers = [parameter for parameter in parameters.keys() if parameter in IDENTIFIERS]
    return get_unique_values(identifiers)

def check_languages(parameters):
    """
    Checks for language values in the given parameters dictionary and returns unique language values.

    Arguments:
        parameters {dict} -- A dictionary containing parameter keys and values.

    Returns:
        {list} -- A list of unique language values found in the parameters.
    """
    languages = [value for parameter, value in parameters.items() if parameter.lower()=="language"]
    return get_unique_values(languages)

def check_categories(client_name, category_table, categories):
    """
    Checks for categories associated with a client in a category table and returns the matching categories.

    Arguments:
        client_name {str} -- The name of the client.
        category_table {object} -- The table object representing the category table.
        categories {list} -- A list of category dictionaries.

    Returns:
        client_categories {list} -- A list of category items matching the client's categories.
    """
    client_categories = []
    for category in categories:
        category_name = category.get("Name")
        found_category = category_table.scan(FilterExpression=Attr('CategoryName').eq(category_name) & Attr('ClientName').eq(client_name))['Items']
        if found_category:
            client_categories += found_category
    return client_categories

def filter_data_language(client_name, language, product_list, category_table):
    """
    Filters data based on the specified client, language, and category information.

    Arguments:
        client_name {str} -- The name of the client.
        language {str} -- The desired language for filtering.
        product_list {list} -- A list of product dictionaries.
        category_table {object} -- The table object representing the category table.

    Returns:
        result {list} -- A list of filtered product dictionaries based on the client, language, and category information.
    """
    result = []
    for product in product_list:
        attributes = []
        filtered_product = product
        categories = [
            category for category in product.get("Categories") if language in category.get("Metadata").get("i18n")
        ]
        descriptions = [
            description for description in product.get("Descriptions") if language in description.get("Metadata").get("i18n")
        ]
        gallery = [
            image for image in product.get("Gallery") if language in image.get("Metadata").get("i18n")
        ]
        for attribute in product.get("Attributes"):
            name = attribute.get("Name")
            label = attribute.get("Label")
            values = [value for value in attribute.get("Values") if language in value.get("Metadata").get("i18n")]
            if values:
                attribute_value = {
                    "Name": name,
                    "Label": label,
                    "Values": values
                }
                attributes.append(attribute_value)

        client_categories = check_categories(client_name, category_table, categories)
        filtered_product.update(
            {
                "Categories": client_categories,
                "Descriptions": descriptions,
                "Gallery": gallery,
                "Attributes": attributes
            }
        )
        result.append(filtered_product)
    return result

def get_filtered_products(client_name, products_table, category_table, parameters):
    """
    Retrieves and filters products based on the specified client, parameters, and language.

    Arguments:
        client_name {str} -- The name of the client.
        products_table {object} -- The table object representing the products table.
        category_table {object} -- The table object representing the category table.
        parameters {dict} -- A dictionary containing parameter keys and values.

    Returns:
        data {str} or {list} or {dict} -- If only one identifier and one language are included in the parameters, the function
                             returns a list of filtered product dictionaries. If there are more than one identifier
                             or language, the function returns an error message. If an invalid parameter is provided,
                             the function returns an error message.
    """
    identifiers_list = check_identifiers_keys(parameters)
    languages_list = check_languages(parameters)
    if len(identifiers_list) >= 2:
        return "Just one identifier must be included"
    if len(languages_list) >= 2:
        return "Just one language must be included"
    language = languages_list[0] if languages_list else "en_US"
    parameters.pop("Language", None)
    parameters.pop("language", None)
    for parameter, value in parameters.items():
        if parameter in IDENTIFIERS:
            response = products_table.scan(FilterExpression=Attr(parameter).contains(value))
            product_list = response["Items"]
            data = filter_data_language(client_name, language, product_list, category_table)
            break
        else:
            data = "Invalid Paremeter: %s" % parameter
    return data

def get_client(client_key, api_keys_register):
    """
    Retrieves the client name associated with the provided client key.

    Arguments:
        client_key {str} -- The client key to search for.
        api_keys_register {object} -- The table object representing the API keys register.

    Returns:
        client_name {str} or {False} -- The client name associated with the client key if found, or False if not found.
    """
    client = api_keys_register.scan(FilterExpression=Attr('api_key').eq(client_key))['Items']
    if client:
        client_name = client[0].get('client_name')
    else:
        client_name = False
    return client_name

def lambda_handler(event, context):
    """
    AWS Lambda function handler for processing client requests.

    Arguments:
        event {dict} -- The event data passed to the Lambda function.
        context {object} -- The context object representing the runtime information.

    Returns:
        {dict} -- The response containing the status code and body.
    """
    data = "Not Found"
    try:
        client_key = event.get('context', {}).get('api-key')
        dynamodb = boto3.resource('dynamodb')
        products_table = dynamodb.Table('test_multithread_db')
        categories_table = dynamodb.Table('data_providers')
        api_keys_register = dynamodb.Table('ClientAPIKeys')
        client_name = get_client(client_key, api_keys_register)
        
        if not client_name:
            return {
                'statusCode': 400,
                'body': json.dumps('This client is not registered')
            }
        
        params = event.get("params", False)
        query_params = params.get("querystring")
        if query_params:
            data = get_filtered_products(client_name, products_table, categories_table, query_params)
        else:
            data = "You must specify the product using the MPN, UPC or EAN"
        return {
            'statusCode': 200,
            'body': data
        }
    except Exception as error:
        return {
            'statusCode': 400,
            'body': json.dumps(error, indent=4)
        }
