import unittest

from orchutils.ibmcloudmodels.accessgroup import AccessGroup

access_group_json = [
    {
        "id": "AccessGroupId-5504t5563563563563456Tsd4",
        "name": "oss-data-science-np-editor"
    }
]


class TestAccessGroup(unittest.TestCase):
    def test_constructor(self):
        access_group = AccessGroup(access_group_json[0])
        self.assertEqual('AccessGroupId-5504t5563563563563456Tsd4', access_group.group_id)
        self.assertEqual('oss-data-science-np-editor', access_group.name)

    def test_properties(self):
        access_group = AccessGroup(access_group_json[0])
        self.assertEqual('AccessGroupId-5504t5563563563563456Tsd4', access_group.group_id)
        access_group.group_id = 'newid'
        self.assertEqual('newid', access_group.group_id)
        access_group.name = 'name'
        self.assertEqual('name', access_group.name)

    def test_parse_access_group(self):
        access_group = AccessGroup.parse_access_groups(access_group_json)
        self.assertEqual(1, len(access_group))
        self.assertEqual('AccessGroupId-5504t5563563563563456Tsd4', access_group[0].group_id)


if __name__ == '__main__':
    unittest.main()
