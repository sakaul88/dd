from orchutils.ibmcloudmodels.attribute import Attribute


class Resource(object):
    def __init__(self, resource_json):
        self.attributes = Attribute.parse_attributes(resource_json['attributes'])

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        self._attributes = attributes

    @classmethod
    def parse_resources(self, resources_json):
        """
        Helper method to parse a list of Resource dictionaries.
        This method simply iterates over the list, instantiating an Resource object for each dictionary.
        Args:
            resources_json: A list of Resource dictionaries from the ibmcloud cli
        Returns: A list of Resource objects
        """
        resources = []
        for resource_json in resources_json:
            resources.append(Resource(resource_json))
        return resources

    def to_json(self):
        """
        Converts the instance into a JSON dictionary.
        """
        return {
            'attributes': self.attributes
        }
