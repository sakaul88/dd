import unittest

from orchutils.ibmcloudmodels.attribute import Attribute

attributes_json = [
    {
        'name': 'accountId',
        'value': '69a92444d0c448d994ceb2f517b2fd39'
    },
    {
        'name': 'serviceName',
        'value': 'cloud-object-storage'
    },
    {
        'name': 'serviceInstance',
        'value': 'cbb40c53-54b5-4747-b1d6-7c83d2d1171b'
    }
]


class TestAttribute(unittest.TestCase):
    def test_constructor(self):
        attribute = Attribute(attributes_json[0])
        self.assertEqual('accountId', attribute.name)
        self.assertEqual('69a92444d0c448d994ceb2f517b2fd39', attribute.value)

    def test_properties(self):
        attribute = Attribute(attributes_json[0])
        self.assertEqual('accountId', attribute.name)
        attribute.name = 'newname'
        self.assertEqual('newname', attribute.name)
        attribute.value = 'value'
        self.assertEqual('value', attribute.value)

    def test_parse_attributes(self):
        attributes = Attribute.parse_attributes(attributes_json)
        self.assertEqual(3, len(attributes))
        self.assertEqual('accountId', attributes[0].name)
        self.assertEqual('serviceName', attributes[1].name)
        self.assertEqual('serviceInstance', attributes[2].name)

    def test_to_json(self):
        attribute = Attribute(attributes_json[0])
        self.assertEqual(attributes_json[0], attribute.to_json())


if __name__ == '__main__':
    unittest.main()
