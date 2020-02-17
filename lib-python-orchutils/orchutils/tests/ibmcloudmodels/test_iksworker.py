import unittest

from orchutils.ibmcloudmodels.iksworker import IKSWorker

workers_json = [
    {
        'privateVlan': '1502303',
        'publicVlan': '',
        'privateIP': '10.168.137.22',
        'publicIP': '',
        'machineType': 'b2c.8x32.encrypted',
        'location': 'sjc03',
        'id': 'kube-sjc03-cra8efa36505be48d0a382aa2fa7081082-w1',
        'state': 'normal',
        'status': 'Ready',
        'statusDate': '',
        'statusDetails': '',
        'errorMessage': '',
        'errorMessageDate': '',
        'isolation': 'public',
        'kubeVersion': '1.13.4_1516',
        'targetVersion': '1.13.5_1517',
        'reasonForDelete': '',
        'versionEOS': '',
        'masterVersionEOS': '',
        'trustedStatus': 'unsupported',
        'poolid': 'a8efa36505be48d0a382aa2fa7081082-863b409',
        'poolName': 'default',
        'pendingOperation': ''
    },
    {
        'privateVlan': '1502303',
        'publicVlan': '',
        'privateIP': '10.168.137.23',
        'publicIP': '',
        'machineType': 'b2c.8x32.encrypted',
        'location': 'sjc03',
        'id': 'kube-sjc03-cra8efa36505be48d0a382aa2fa7081082-w2',
        'state': 'normal',
        'status': 'Ready',
        'statusDate': '',
        'statusDetails': '',
        'errorMessage': '',
        'errorMessageDate': '',
        'isolation': 'public',
        'kubeVersion': '1.13.4_1516',
        'targetVersion': '1.13.5_1517',
        'reasonForDelete': '',
        'versionEOS': '',
        'masterVersionEOS': '',
        'trustedStatus': 'unsupported',
        'poolid': 'a8efa36505be48d0a382aa2fa7081082-863b409',
        'poolName': 'default',
        'pendingOperation': ''
    }
]


class TestIKSWorker(unittest.TestCase):
    def test_constructor(self):
        worker = IKSWorker(workers_json[0])
        self.assertEqual('kube-sjc03-cra8efa36505be48d0a382aa2fa7081082-w1', worker.id)
        self.assertEqual('normal', worker.state)
        self.assertEqual('Ready', worker.status)
        self.assertEqual('10.168.137.22', worker.private_ip)
        self.assertEqual('', worker.public_ip)
        self.assertEqual('b2c.8x32.encrypted', worker.machine_type)
        self.assertEqual('sjc03', worker.location)
        self.assertEqual('default', worker.pool_name)
        self.assertEqual('1.13.4_1516', worker.kube_version)
        self.assertEqual('1.13.5_1517', worker.target_version)
        self.assertEqual('', worker.pending_operation)

    def test_properties(self):
        worker = IKSWorker(workers_json[0])
        self.assertEqual('kube-sjc03-cra8efa36505be48d0a382aa2fa7081082-w1', worker.id)
        worker.id = 'newid'
        self.assertEqual('newid', worker.id)
        worker.state = 'state'
        self.assertEqual('state', worker.state)
        worker.status = 'status'
        self.assertEqual('status', worker.status)
        worker.private_ip = '1.0.1.0'
        self.assertEqual('1.0.1.0', worker.private_ip)
        worker.public_ip = '2.0.2.0'
        self.assertEqual('2.0.2.0', worker.public_ip)
        worker.machine_type = 'machine_type'
        self.assertEqual('machine_type', worker.machine_type)
        worker.location = 'wdc04'
        self.assertEqual('wdc04', worker.location)
        worker.pool_name = 'edge'
        self.assertEqual('edge', worker.pool_name)
        worker.kube_version = 'kversion'
        self.assertEqual('kversion', worker.kube_version)
        worker.target_version = 'tversion'
        self.assertEqual('tversion', worker.target_version)
        worker.pending_operation = 'reload'
        self.assertEqual('reload', worker.pending_operation)

    def test_parse_iks_worker(self):
        workers = IKSWorker.parse_iks_workers(workers_json)
        self.assertEqual(2, len(workers))
        self.assertEqual('kube-sjc03-cra8efa36505be48d0a382aa2fa7081082-w1', workers[0].id)
        self.assertEqual('kube-sjc03-cra8efa36505be48d0a382aa2fa7081082-w2', workers[1].id)


if __name__ == '__main__':
    unittest.main()
