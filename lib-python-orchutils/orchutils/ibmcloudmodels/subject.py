from orchutils.ibmcloudmodels.attribute import Attribute


class Subject(object):
    def __init__(self, subject_json):
        self.attributes = Attribute.parse_attributes(subject_json['attributes'])

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        self._attributes = attributes

    @classmethod
    def parse_subjects(self, subjects_json):
        """
        Helper method to parse a list of Subject dictionaries.
        This method simply iterates over the list, instantiating an Subject object for each dictionary.
        Args:
            subjects_json: A list of Subject dictionaries from the ibmcloud cli
        Returns: A list of Subject objects
        """
        subjects = []
        for subject_json in subjects_json:
            subjects.append(Subject(subject_json))
        return subjects

    def to_json(self):
        """
        Converts the instance into a JSON dictionary.
        """
        return {
            'attributes': self.attributes
        }
