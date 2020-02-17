import unittest

from orchutils.ibmcloudmodels.region import Region

region_json = {
    'mccp_id': '',
    'name': 'n'
}


class TestRegion(unittest.TestCase):
    def test_constructor(self):
        region = Region(region_json)
        self.assertEqual('', region.mccp_id)
        self.assertEqual('n', region.name)

    def test_properties(self):
        region = Region(region_json)
        self.assertEqual('', region.mccp_id)
        region.mccp_id = 'mccp'
        self.assertEqual('mccp', region.mccp_id)
        region.name = 'name'
        self.assertEqual('name', region.name)


if __name__ == '__main__':
    unittest.main()
