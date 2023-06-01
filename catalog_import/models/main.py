from .connection import Connection
from .provider import Provider
from .products import Products


class Main:
    def __init__(self, **kwargs) -> None:
        self.provider_name = kwargs.get("provider_name")
        self.provider_values = kwargs.get("provider_values")

    def create_provider(self):
        """
        Creates the provider's object

        Arguments:
            values {dict} -- The values dict to create the provider's object

        Returns:
            {object} -- Provider's object

        """
        return Provider(self.provider_values)

    def create_connection(self):
        """
        Creates the connection's object

        Arguments:
            provider_values {dict} -- The providers values dict to create the provider's connection

        Returns:
            {object} -- Connection's object

        """
        provider = self.create_provider()
        return Connection(provider=provider)

    def get_provider_response(self):
        """
        Get the dictionary result of the provider's connection

        Arguments:
            connection {object} -- The connection's object

        Returns:
            {dict} -- Response dict of the provider's connection

        """
        connection = self.create_connection()
        return connection.response_dict()

    def create_product(self, **kwargs):
        """
        Creates the product's object

        Arguments:
            values {dict} -- The values dict to create the product's object

        Returns:
            {object} -- Provider's object

        """
        return Products(**kwargs)

    def execute(self):
        products = []
        response = self.get_provider_response()
        product = self.create_product(response=response)
        if self.provider_name.startswith("Icecat"):
            products = product.parse_response_icecat()
        elif self.provider_name.startswith("Etilize"):
            products = product.parse_response_etilize()
        print(len(products))
