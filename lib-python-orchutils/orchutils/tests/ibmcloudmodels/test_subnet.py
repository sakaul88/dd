import unittest

from orchutils.ibmcloudmodels.subnet import Subnet

subnets_json = [
    {
        'id': '1970265',
        'type': 'private',
        'vlan_id': '2466991',
        'ip_addresses': [],
        'properties': {
            'cidr': '29',
            'network_identifier': '10.211.13.120',
            'note': 'note-content',
            'subnet_type': 'secondary_on_vlan',
            'display_label': '10.211.13.120/29',
            'gateway': '10.211.13.121',
            'bound_cluster': '',
            'datacenter': ''
        }
    },
    {
        'id': '1922973',
        'type': 'public',
        'vlan_id': '2500855',
        'ip_addresses': [],
        'properties': {
            'cidr': '29',
            'network_identifier': '52.116.9.64',
            'note': 'iks-platform-hub-pr-dal',
            'subnet_type': 'secondary_on_vlan',
            'display_label': '52.116.9.64/29',
            'gateway': '52.116.9.65',
            'bound_cluster': '0af092f8be004c79b7105f92105a3b6f',
            'datacenter': ''
        }
    }
]


class TestSubnet(unittest.TestCase):
    def test_constructor(self):
        subnet = Subnet(subnets_json[0])
        self.assertEqual('1970265', subnet.id)
        self.assertEqual('private', subnet.type)
        self.assertEqual('2466991', subnet.vlan_id)
        self.assertEqual('', subnet.bound_cluster)
        self.assertEqual('note-content', subnet.note)

    def test_properties(self):
        subnet = Subnet(subnets_json[0])
        self.assertEqual('1970265', subnet.id)
        subnet.id = 'newid'
        self.assertEqual('newid', subnet.id)
        subnet.type = 'public'
        self.assertEqual('public', subnet.type)
        subnet.vlan_id = 'vlan_id'
        self.assertEqual('vlan_id', subnet.vlan_id)
        subnet.bound_cluster = 'clusterid'
        self.assertEqual('clusterid', subnet.bound_cluster)
        subnet.note = 'note'
        self.assertEqual('note', subnet.note)

    def test_parse_subnets(self):
        subnets = Subnet.parse_subnets(subnets_json)
        self.assertEqual(2, len(subnets))
        self.assertEqual('1970265', subnets[0].id)
        self.assertEqual('1922973', subnets[1].id)


if __name__ == '__main__':
    unittest.main()
