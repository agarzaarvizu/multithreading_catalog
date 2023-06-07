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
    values_list = []
    for value in values:
        values_list += value.split(",")
    return list(set(values_list))

def check_identifiers_keys(parameters):
    identifiers = [parameter for parameter in parameters.keys() if parameter in IDENTIFIERS]
    return get_unique_values(identifiers)

def check_languages(parameters):
    languages = [value for parameter, value in parameters.items() if parameter.lower()=="language"]
    return get_unique_values(languages)

def filter_data_language(language, product_list):
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

        filtered_product.update(
            {
                "Categories": categories,
                "Descriptions": descriptions,
                "Gallery": gallery,
                "Attributes": attributes
            }
        )
        result.append(filtered_product)
    return result

def get_filtered_products(table, parameters):
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
            response = table.scan(FilterExpression=Attr(parameter).contains(value))
            product_list = response["Items"]
            data = filter_data_language(language, product_list)
            break
        else:
            data = "Invalid Paremeter: %s" % parameter
    return data

def lambda_handler(event, context):
    data = "Not Found"
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('test_multithread_db')
        params = event.get("params", False)
        query_params = params.get("querystring")
        if query_params:
            data = get_filtered_products(table, query_params)
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
