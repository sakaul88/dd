import unittest

from orchutils.ibmcloudmodels.zone import Zone

zones_json = [
    {
        'privateVlan': '2342855',
        'publicVlan': '',
        'id': 'wdc04',
        'workerCount': 3
    },
    {
        'privateVlan': '2342856',
        'publicVlan': '',
        'id': 'wdc06',
        'workerCount': 3
    }
]


class TestZone(unittest.TestCase):
    def test_constructor(self):
        zone = Zone(zones_json[0])
        self.assertEqual('wdc04', zone.id)
        self.assertEqual('2342855', zone.private_vlan)
        self.assertEqual('', zone.public_vlan)
        self.assertEqual(3, zone.worker_count)

    def test_properties(self):
        zone = Zone(zones_json[0])
        self.assertEqual('wdc04', zone.id)
        zone.id = 'newid'
        self.assertEqual('newid', zone.id)
        zone.private_vlan = 'private_vlan'
        self.assertEqual('private_vlan', zone.private_vlan)
        zone.public_vlan = 'public_vlan'
        self.assertEqual('public_vlan', zone.public_vlan)
        zone.worker_count = 5
        self.assertEqual(5, zone.worker_count)

    def test_parse_zones(self):
        zones = Zone.parse_zones(zones_json)
        self.assertEqual(2, len(zones))
        self.assertEqual('wdc04', zones[0].id)
        self.assertEqual('wdc06', zones[1].id)


if __name__ == '__main__':
    unittest.main()
