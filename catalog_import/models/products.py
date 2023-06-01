class Products:
    def __init__(self, **kwargs) -> None:
        self.response = kwargs.get("response", False)

    def parse_response_icecat(self):
        products = list()
        products_response = self.response["Products"]["Product"] if self.response else []
        for product in products_response:
            ean_value = product.get("EANS", {}).get("EAN")
            ean = [ean_value] if isinstance(ean_value, str) else ean_value
            attributes_dict = product.get("Attributes", {}).get("Attribute", [])

            product_values = {
                "MPN": product.get("MPN", False),
                "EANS": ean,
                "SKU": product.get("SKU", False),
                "Categories": [
                    {
                        "ID": product.get("Category", {}).get("CategoryID"),
                        "Name": product.get("Category", {}).get("CategoryName"),
                    }
                ] if product.get("Category") else [],
                "Descriptions": [
                    {
                        "1": product.get("Description", {}).get("ProductName", False),
                        "2": product.get("Description", {}).get("ShortSummaryDescription", False),
                        "3": product.get("Description", {}).get("ShortDescription", False),
                        "4": product.get("Description", {}).get("LongDescription", False),
                    }
                ],
                "Gallery": [
                    {"Value": product.get("Images", {}).get("ImageLink", [])}
                ],
                "Attributes": [
                    {
                        "Name": attribute["Name"],
                        "Label": attribute["Label"],
                        "Values": [{"Value": attribute["Value"]}],
                    }
                    for attribute in attributes_dict
                ]
            }

            products.append(product_values)
        return products

    def parse_response_etilize(self):
        products = list()
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
            for identifier in identifiers_list:
                identifier_name = identifier.get("@type")
                identifier_value = identifier.get("@number")
                if identifier_name in valid_identifiers:
                    identifier_name = "MPN" if identifier_name == "MFGPARTNUMBER" else identifier_name
                    if identifier_name == "EAN":
                        identifier_value = (
                            [identifier_value] if isinstance(identifier_value, str) else identifier_value
                        )
                    product_values[identifier_name] = identifier_value



            descriptions_dict = product.get("descriptions", {})
            descriptions_list = descriptions_dict.get("description", [])[1:]
            for description in descriptions_list:
                description_name = description.get("@type")
                description_value = description.get("#text")
                descriptions[description_name] = description_value

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
                            "Values": [{"Value": attribute_value}],
                        }
                    )



            product_values.update(
                {
                    "Categories": {
                        "ID": category_values.get("@id"),
                        "Name": category_values.get("@name"),
                    },
                    "Descriptions": [
                        descriptions
                    ],
                    "Attributes": attributes_list
                }
            )
            products.append(product_values)
        return products
