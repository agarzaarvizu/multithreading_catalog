providers = {
    "Icecat": {
        "name": "Icecat",
        "url": False,
        "filepath": "catalog_import/data/files/IcecatProductsExampleEN.xml",
        "connection_type": "file",
        "response_type": "file",
        "products_list": False,
        "locations": [
            {"location_tag": "en_US", "location_label": "English"},
        ],
    },
    "IcecatES": {
        "name": "IcecatES",
        "url": False,
        "filepath": "catalog_import/data/files/IcecatProductsExampleES.xml",
        "connection_type": "file",
        "response_type": "file",
        "products_list": False,
        "locations": [
            {"location_tag": "es_MX", "location_label": "Spanish"},
        ],
    },
    "Etilize": {
        "name": "Etilize",
        "url": "https://sellerapp.generalprocurement.com/web/etilize/request?appId=226671&catalog=na&method=getProduct&locale=en_us&mfgId=10753&partNumber=%s&descriptionTypes=all&categories=default&manufacturer=default&displayTemplate=0&categorizeAccessories=false&skuType=all&resourceTypes=all",
        "filepath": False,
        "connection_type": "api",
        "response_type": "xml",
        "products_list": "catalog_import/data/files/EtilizeProductsMPNList.json",
        "locations": [
            {"location_tag": "en_US", "location_label": "English"},
        ],
    },
}
