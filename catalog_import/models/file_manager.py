import os
import xmltodict
import xml.etree.ElementTree as ET


class FileManager:
    """
    A class used to represent the file management
    ...

    Attributes:
        filepath {string} -- The filepath of the file

    Methods:
        file_exists() -- Check if a file exists
        xml_to_dict() -- Parse the XML file and create a dictionary
        parse_file_response() -- Main method to parse the file

    """
    def __init__(self, **kwargs) -> None:
        """
        Parameters:
            filepath {string} -- The filepath of the file

        """
        self.filepath = kwargs.get("filepath", False)

    def file_exists(self):
        """
        Check if the file exists

        Returns:
            {Bool} -- True or False depending if the file exists

        """
        return os.path.isfile(self.filepath)

    def xml_file_to_dict(self):
        """
        Parse the XML file to convert it to a dictionary

        Returns:
            {dict} -- The XML converted to a dictonary

        """
        tree = ET.parse(self.filepath)
        root = tree.getroot()
        xmlstr = ET.tostring(root, encoding="utf-8", method="xml")
        return xmltodict.parse(xmlstr)

    def parse_file_response(self):
        """
        Main method to parse the file

        Returns:
            response_dict {dict} -- The response file converted to a dictionary

        """
        if self.filepath.endswith(".xml"):  # If the file is an XML
            response = self.xml_file_to_dict()
        else:  # TODO: Add more functions in order to manage different file types
            response = {}
        return response
