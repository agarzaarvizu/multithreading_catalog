from boto3.dynamodb.conditions import Attr


class Products:
    def __init__(self, **kwargs) -> None:
        self.response = kwargs.get("response", False)
        self.db_table = kwargs.get("db_table")
        self.metadata = kwargs.get("metadata")

    def create(self, **kwargs):
        print("Product Created: ", kwargs.get("product").get("MPN"))
        self.db_table.put_item(Item=kwargs.get("product"))

    def update(self, **kwargs):
        product_found = kwargs.get("product_found")
        product = kwargs.get("product")
        
        new_values = set(product) - set(product_found)

        new_values_dict = {}
        new_values_update = "SET "
        for new_value in new_values:
            new_values_dict[":" + new_value.lower()] = product.get(new_value)
            if new_value != list(new_values)[-1]:
                new_values_update += "%s = :%s, " % (new_value, new_value.lower())
            else:
                new_values_update += "%s = :%s" % (new_value, new_value.lower())

        categories_found_list = [category.get("Name") for category in product_found.get("Categories")]
        categories = product_found.get("Categories").copy()
        for category in product.get("Categories"):
            if not category.get("Name") in categories_found_list:
                categories.append(category)
        if categories != product_found.get("Categories"):
            new_values_dict[":categories"] = categories
            if new_values_update != "SET ":
                new_values_update += ", Categories = :categories"
            else:
                new_values_update += "Categories = :categories"

        descriptions_providers = [description.get("Provider") for description in product_found.get("Descriptions")]
        descriptions = product_found.get("Descriptions").copy()
        for description in product.get("Descriptions"):
            if not description.get("Provider") in descriptions_providers:
                descriptions.append(description)
        if descriptions != product_found.get("Descriptions"):
            new_values_dict[":descriptions"] = descriptions
            if new_values_update != "SET ":
                new_values_update += ", Descriptions = :descriptions"
            else:
                new_values_update += "Descriptions = :descriptions"

        attributes_registered = [attribute.get("Label") for attribute in product_found.get("Attributes")]
        attributes = product_found.get("Attributes").copy()
        for attribute in product.get("Attributes"):
            if not attribute.get("Label") in attributes_registered:
                attributes.append(attribute)
        if attributes != product_found.get("Attributes"):
            new_values_dict[":attributes"] = attributes
            if new_values_update != "SET ":
                new_values_update += ", Attributes = :attributes"
            else:
                new_values_update += "Attributes = :attributes"

        eans = product_found.get("EAN").copy()
        for ean in product.get("EAN"):
            if not ean in eans:
                eans.append(ean)
        if eans != product_found.get("EAN"):
            new_values_dict[":eans"] = eans
            if new_values_update != "SET ":
                new_values_update += ", EAN = :eans"
            else:
                new_values_update += "EAN = :eans"

        if new_values_dict:
            print("Product Updated: ", product_found.get("MPN"))
            self.db_table.update_item(
                Key={
                    'MPN': product_found.get("MPN"),
                },
                UpdateExpression=new_values_update,
                ExpressionAttributeValues=new_values_dict,
                ReturnValues="UPDATED_NEW"
            )

    def upsert_products(self, **kwargs):
        response = self.db_table.scan(FilterExpression=Attr("MPN").eq(kwargs.get("mpn")))
        count = response.get("Count")
        if count == 0:
            self.create(**kwargs)
        else:
            kwargs["product_found"] = response.get("Items")[0]
            self.update(**kwargs)

    def parse_response_icecat(self):
        products_response = self.response["Products"]["Product"] if self.response else []
        for product in products_response:
            ean_value = product.get("EANS", {}).get("EAN")
            ean = [ean_value] if isinstance(ean_value, str) else ean_value
            attributes_dict = product.get("Attributes", {}).get("Attribute", [])
            sku = [product.get("SKU", False)] if isinstance(product.get("SKU", False), str) else product.get("SKU", False)

            product_values = {
                "MPN": product.get("MPN", False),
                "EAN": ean if ean else [],
                "SKU": sku,
                "Categories": [
                    {
                        "ID": product.get("Category", {}).get("CategoryID"),
                        "Name": product.get("Category", {}).get("CategoryName"),
                        "Metadata": self.metadata,
                    }
                ] if product.get("Category") else [],
                "Descriptions": [
                    {
                        "1": product.get("Description", {}).get("ProductName", False),
                        "2": product.get("Description", {}).get("ShortSummaryDescription", False),
                        "3": product.get("Description", {}).get("ShortDescription", False),
                        "4": product.get("Description", {}).get("LongDescription", False),
                        "Metadata": self.metadata
                    }
                ],
                "Gallery": [
                    {
                        "Value": product.get("Images", {}).get("ImageLink", []),
                        "Metadata": self.metadata,
                    }
                ],
                "Attributes": [
                    {
                        "Name": attribute["Name"],
                        "Label": attribute["Label"],
                        "Values": [{"Value": attribute["Value"], "Metadata": self.metadata}],
                    }
                    for attribute in attributes_dict
                ]
            }
            
            self.upsert_products(mpn=product_values.get("MPN"), product=product_values)


    def parse_response_etilize(self):
        valid_identifiers = [
            "MFGPARTNUMBER",
            "EAN",
            "UPC",
            "GTIN"
        ]
        for product_response in self.response:
            product_values = dict()
            descriptions = dict()
            attributes_list = list()
            product = product_response.get("Product")
            identifiers_list = product.get("skus", {}).get("sku", [])
            identifiers_metadata = self.metadata.copy()
            identifiers_metadata.pop("i18n", None)
            for identifier in identifiers_list:
                identifier_name = identifier.get("@type")
                identifier_value = identifier.get("@number")
                if identifier_name in valid_identifiers:
                    identifier_name = "MPN" if identifier_name == "MFGPARTNUMBER" else identifier_name
                    main_identifiers = ["EAN", "GTIN", "UPC"]
                    if identifier_name in main_identifiers:
                        identifier_value = (
                            [identifier_value] if isinstance(identifier_value, str) else identifier_value
                        )
                        product_values[identifier_name] = identifier_value
                    else:
                        product_values[identifier_name] = {
                            "Value": identifier_value,
                            "Metadata": identifiers_metadata,
                        } if identifier_name != "MPN" else identifier_value



            descriptions_dict = product.get("descriptions", {})
            descriptions_list = descriptions_dict.get("description", [])[1:]
            for description in descriptions_list:
                description_name = description.get("@type")
                description_value = description.get("#text")
                descriptions[description_name] = description_value
            
            descriptions["Metadata"] = self.metadata

            category_values = product.get("category", {})

            datasheet = product.get("datasheet", {}).get("attributeGroup", [])
            for group in datasheet:
                attributes = group.get("attribute", [])
                if not isinstance(attributes, list):
                    attributes = [attributes]
                for attribute in attributes:
                    attribute_name = attribute.get("@name")
                    attribute_label = attribute_name.lower().replace(" ", "_")
                    attribute_value = attribute.get("#text")
                    attributes_list.append(
                        {
                            "Name": attribute_name,
                            "Label": attribute_label,
                            "Values": [{"Value": attribute_value, "Metadata": self.metadata}],
                        }
                    )



            product_values.update(
                {
                    "Categories": [
                        {
                            "ID": category_values.get("@id"),
                            "Name": category_values.get("@name"),
                            "Metadata": self.metadata,
                        }
                    ],
                    "Descriptions": [
                        descriptions
                    ],
                    "Attributes": attributes_list
                }
            )
            self.upsert_products(mpn=product_values.get("MPN"), product=product_values)
