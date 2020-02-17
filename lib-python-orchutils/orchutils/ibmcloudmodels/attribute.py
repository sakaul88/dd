class Attribute(object):
    def __init__(self, attribute_json):
        self.name = attribute_json['name']
        self.value = attribute_json['value']

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @classmethod
    def parse_attributes(self, attributes_json):
        """
        Helper method to parse a list of Attribute dictionaries.
        This method simply iterates over the list, instantiating an Attribute object for each dictionary.
        Args:
            attributes_json: A list of Attribute dictionaries from the ibmcloud cli
        Returns: A list of Attribute objects
        """
        attributes = []
        for attribute_json in attributes_json:
            attributes.append(Attribute(attribute_json))
        return attributes

    def to_json(self):
        return {
            'name': self.name,
            'value': self.value
        }
