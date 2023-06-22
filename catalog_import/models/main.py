from .connection import Connection
from .provider import Provider
from .products import Products


class Main:
    """
    A class used to represent the main class
    ...

    Attributes:
        provider_name {str} -- The provider's name
        provider_values {dict} -- The provider's values
        db_table {object} -- The product's db table
        metadata {dict} -- The metadata of the connection

    Methods:
        create_provider() -- Creates the provider's object
        create_connection() -- Creates the connection's object
        get_provider_response() -- Get the dictionary result of the provider's connection
        create_product() -- Creates the product's object
        execute() -- Executes the main execution logic for processing the provider response and parsing the product data

    """
    def __init__(self, **kwargs) -> None:
        """
        Parameters:
            provider_name {str} -- The provider's name
            provider_values {dict} -- The provider's values
            db_table {object} -- The product's db table
            metadata {dict} -- The metadata of the connection

        """
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
        """
        Executes the main execution logic for processing the provider response and parsing the product data.

        This method retrieves the provider's response using the `get_provider_response` method.
        It then creates a product object using the retrieved response, the database table object, and the metadata.
        Depending on the provider name, the method calls the appropriate parsing method to parse the response
        and update the product data accordingly.

        Returns:
            None
        """
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
