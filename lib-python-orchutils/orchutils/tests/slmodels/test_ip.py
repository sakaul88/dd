import unittest

from orchutils.slmodels.ip import IP


class TestIP(unittest.TestCase):
    def test_constructor(self):
        ip = IP(10, {'subnetId': 123, 'ipAddress': '1.1.1.1'})
        self.assertEqual(10, ip.id)
        self.assertEqual(123, ip.subnet_id)
        self.assertEqual('1.1.1.1', ip.address)
        self.assertEqual('', ip.note)
        self.assertEqual(False, ip.network)
        self.assertEqual(False, ip.gateway)
        self.assertEqual(False, ip.broadcast)
        self.assertEqual(False, ip.reserved)
        ip = IP(11, {'subnetId': 124, 'ipAddress': '1.1.1.2', 'note': 'my note', 'isGateway': True, 'isBroadcast': False})
        self.assertEqual(11, ip.id)
        self.assertEqual(124, ip.subnet_id)
        self.assertEqual('1.1.1.2', ip.address)
        self.assertEqual('my note', ip.note)
        self.assertEqual(False, ip.network)
        self.assertEqual(True, ip.gateway)
        self.assertEqual(False, ip.broadcast)
        self.assertEqual(False, ip.reserved)
        ip = IP(11, {'subnetId': 123, 'ipAddress': '1.1.1.2', 'isBroadcast': True})
        self.assertEqual(False, ip.network)
        self.assertEqual(False, ip.gateway)
        self.assertEqual(True, ip.broadcast)
        self.assertEqual(False, ip.reserved)
        ip = IP(11, {'subnetId': 123, 'ipAddress': '1.1.1.2', 'isNetwork': True})
        self.assertEqual(True, ip.network)
        self.assertEqual(False, ip.gateway)
        self.assertEqual(False, ip.broadcast)
        self.assertEqual(False, ip.reserved)
        ip = IP(11, {'subnetId': 123, 'ipAddress': '1.1.1.2', 'isReserved': True})
        self.assertEqual(False, ip.network)
        self.assertEqual(False, ip.gateway)
        self.assertEqual(False, ip.broadcast)
        self.assertEqual(True, ip.reserved)

    def test_properties(self):
        ip = IP(10, {'subnetId': 123, 'ipAddress': '1.1.1.1'})
        self.assertEqual(10, ip.id)
        ip.id = 12
        self.assertEqual(12, ip.id)
        ip.subnet_id = 125
        self.assertEqual(125, ip.subnet_id)
        ip.address = '2.2.2.2'
        self.assertEqual('2.2.2.2', ip.address)
        ip.note = 'a test note'
        self.assertEqual('a test note', ip.note)
        ip.network = True
        self.assertEqual(True, ip.network)
        ip.network = False
        ip.gateway = True
        self.assertEqual(False, ip.network)
        self.assertEqual(True, ip.gateway)
        ip.gateway = False
        ip.broadcast = True
        self.assertEqual(False, ip.gateway)
        self.assertEqual(True, ip.broadcast)
        ip.broadcast = False
        ip.reserved = True
        self.assertEqual(False, ip.broadcast)
        self.assertEqual(True, ip.reserved)

    def test_equals(self):
        ip1 = IP(10, {'subnetId': 123, 'ipAddress': '1.1.1.1', 'note': 'my note', 'isGateway': True})
        ip2 = IP(10, {'subnetId': 123, 'ipAddress': '1.1.1.1', 'note': 'my note', 'isGateway': True})
        self.assertEqual(ip1, ip2)
        ip1.reserved = True
        self.assertNotEqual(ip1, ip2)
        ip2.reserved = True
        self.assertEqual(ip1, ip2)
        ip3 = IP(11, {'subnetId': 123, 'ipAddress': '1.1.1.2'})
        self.assertNotEqual(ip1, ip3)


if __name__ == '__main__':
    unittest.main()
