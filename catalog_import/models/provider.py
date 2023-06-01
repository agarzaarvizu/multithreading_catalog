class Provider:
    """
    A class used to represent the provider
    ...

    Attributes:
        in_dict {dict} -- The dict with the provider's attributes

    """

    def __init__(self, in_dict: dict):
        """
        Create the attributes based on the keys in the dict

        Parameters:
            in_dict {dict} -- The dict with the provider's attributes

        """
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
                setattr(self, key, [Provider(x) if isinstance(x, dict) else x for x in val])
            else:
                setattr(self, key, Provider(val) if isinstance(val, dict) else val)
