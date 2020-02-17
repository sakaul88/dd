import unittest

from orchutils.slmodels.ip import IP
from orchutils.slmodels.subnet import Subnet


class TestSubnet(unittest.TestCase):
    def test_constructor(self):
        subnet_json = {
            'cidr': 24,
            'networkIdentifier': '1.1.1.0',
            'networkVlanId': 1234,
            'ipAddresses': [
                {'id': 0, 'subnetId': 1, 'ipAddress': '1.1.1.0', 'isNetwork': True},
                {'id': 1, 'subnetId': 1, 'ipAddress': '1.1.1.1'},
                {'id': 2, 'subnetId': 1, 'ipAddress': '1.1.1.2'},
                {'id': 3, 'subnetId': 1, 'ipAddress': '1.1.1.3', 'note': 'host3'},
                {'id': 4, 'subnetId': 1, 'ipAddress': '1.1.1.4', 'note': 'host4'},
                {'id': 5, 'subnetId': 1, 'ipAddress': '1.1.1.5', 'note': 'host5', 'isReserved': True},
                {'id': 6, 'subnetId': 1, 'ipAddress': '1.1.1.6'}
            ]
        }
        subnet = Subnet(1, subnet_json)
        self.assertEqual(1, subnet.id)
        self.assertEqual('1.1.1.0/24', subnet.cidr)
        self.assertEqual(1234, subnet.vlan_id)
        self.assertEqual(7, len(subnet.ips))
        self.assertEqual(3, len(subnet.ips_available))
        self.assertEqual(2, len(subnet.ips_inuse))
        self.assertEqual(1, subnet.ips_available[0].id)
        self.assertEqual(6, subnet.ips_available[2].id)
        inuse_keys = list(subnet.ips_inuse.keys())
        inuse_keys.sort()
        self.assertEqual(['host3', 'host4'], inuse_keys)

    def test_properties(self):
        subnet = Subnet(1, {'ipAddresses': [], 'cidr': 24, 'networkIdentifier': '1.1.1.0', 'networkVlanId': 1234})
        self.assertEqual(1, subnet.id)
        subnet.id = 2
        self.assertEqual(2, subnet.id)
        subnet.cidr = '2.2.2.0/24'
        self.assertEqual('2.2.2.0/24', subnet.cidr)
        subnet.vlan_id = 10
        self.assertEqual(10, subnet.vlan_id)
        ips = [IP(0, {'subnetId': 123, 'id': 0, 'ipAddress': '1.1.1.1'})]
        subnet.ips = ips
        self.assertEqual(ips, subnet.ips)
        subnet.ips_available = ips
        self.assertEqual(ips, subnet.ips_available)
        subnet.ips_inuse = ips
        self.assertEqual(ips, subnet.ips_inuse)

    def test_equals(self):
        subnet1 = Subnet(1, {'ipAddresses': [], 'cidr': 24, 'networkIdentifier': '1.1.1.0', 'networkVlanId': 1234})
        subnet2 = Subnet(1, {'ipAddresses': [], 'cidr': 24, 'networkIdentifier': '1.1.1.0', 'networkVlanId': 1234})
        self.assertEqual(subnet1, subnet2)
        subnet1.ips.append(IP(0, {'subnetId': 123, 'id': 0, 'ipAddress': '1.1.1.1'}))
        self.assertNotEqual(subnet1, subnet2)
        subnet2.ips.append(IP(0, {'subnetId': 123, 'id': 0, 'ipAddress': '1.1.1.1'}))
        self.assertEqual(subnet1, subnet2)
        subnet3 = Subnet(2, {'ipAddresses': [], 'cidr': 24, 'networkIdentifier': '1.1.1.0', 'networkVlanId': 1234})
        self.assertNotEqual(subnet1, subnet3)


if __name__ == '__main__':
    unittest.main()
