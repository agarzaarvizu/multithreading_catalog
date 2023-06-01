import json
import requests
import xmltodict
from .file_manager import FileManager


class Connection:
    """
    A class used to represent the provider's connection
    ...

    Attributes:
        user {string} -- The username for the connection
        password {string} -- The password for the connection
        provider {object} -- The provider related to the connection

    Methods:
        xml_to_dict_response(response) -- Convert the XML response to dict
        get_metadata_connection() -- Get the metadata of the connection
        response_request() -- Get the API response to the provider's request
        response_dict() -- Get the response dict to the provider's request

    """

    def __init__(self, **kwargs) -> None:
        self.provider = kwargs.get("provider")

    def xml_to_dict_response(self, response):
        """
        Convert the XML reponse to a dictionary

        Arguments:
            response {string} -- The connection XML response

        Returns:
            {dict} -- Response converted to a dictionary

        """
        return xmltodict.parse(response)

    def connection_products_list(self):
        file = open(self.provider.products_list)
        data = json.load(file)
        products_list = [product for product in data]
        file.close()
        return products_list

    def get_request(self, product):
        url = self.provider.url
        request_url = url % product
        response = requests.get(request_url)
        if response.status_code == 200:
            request_result = self.xml_to_dict_response(response.text) if self.provider.response_type=="xml" else json.loads(response.text)
        else:
            request_result = {}
        return request_result

    def response_request(self):
        """
        Get the API response to the provider's request

        Returns:
            {dict} -- Dict response

        """
        if self.provider.products_list:
            result = []
            products_list = self.connection_products_list()
            for product in products_list:
                request_result = self.get_request(product=product)
                if request_result and not request_result.get("ErrorResponse", False):
                    result.append(request_result)
        return result

    def response_dict(self):
        """
        Get the response dict to the provider's request

        Returns:
            result {dict} -- The result to the connection

        """
        if self.provider.connection_type == "file":  # If the connection returns a file
            file_manager = FileManager(
                filepath = self.provider.filepath
            )  # Creating a FileManager object to manage the file response
            response = file_manager.parse_file_response()
        elif self.provider.connection_type == "api":  # If the connection is to an API
            response = self.response_request()
        return response
