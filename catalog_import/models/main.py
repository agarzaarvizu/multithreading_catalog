from .connection import Connection
from .provider import Provider
from .products import Products


class Main:
    def __init__(self, **kwargs) -> None:
        self.provider_name = kwargs.get("provider_name")
        self.provider_values = kwargs.get("provider_values")
        self.db_table = kwargs.get("db_table")
        self.metadata = kwargs.get("metadata")

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
        response = self.get_provider_response()
        product = self.create_product(
            response=response,
            db_table=self.db_table,
            metadata=self.metadata
        )
        if self.provider_name.startswith("Icecat"):
            product.parse_response_icecat()
        elif self.provider_name.startswith("Etilize"):
            product.parse_response_etilize()
