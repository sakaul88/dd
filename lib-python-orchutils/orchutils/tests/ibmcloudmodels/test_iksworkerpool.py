import unittest

from orchutils.ibmcloudmodels.iksworkerpool import IKSWorkerPool

worker_pools_json = [
    {
        'name': 'edge',
        'sizePerZone': 2,
        'machineType': 'b2c.4x16.encrypted',
        'isolation': 'public',
        'labels': {
            'dedicated': 'edge',
            'ibm-cloud.kubernetes.io/worker-pool-id': 'bm12clsw08k9uctrq8cg-d423e5a',
            'kubernetes.io/role': 'edge'
        },
        'id': 'bm12clsw08k9uctrq8cg-d423e5a',
        'region': 'us-east',
        'state': 'active',
        'reasonForDelete': '',
        'isBalanced': True,
        'autoscaleEnabled': False,
        'zones': [
            {
                'privateVlan': '2342855',
                'publicVlan': '2342853',
                'id': 'wdc04',
                'workerCount': 2
            }
        ]
    },
    {
        'name': 'default',
        'sizePerZone': 3,
        'machineType': 'b2c.8x32.encrypted',
        'isolation': 'public',
        'labels': {
            'ibm-cloud.kubernetes.io/worker-pool-id': 'bm12clsw08k9uctrq8cg-d7e1428'
        },
        'id': 'bm12clsw08k9uctrq8cg-d7e1428',
        'region': 'us-east',
        'state': 'active',
        'reasonForDelete': '',
        'isBalanced': True,
        'autoscaleEnabled': False,
        'zones': [
            {
                'privateVlan': '2342855',
                'publicVlan': '',
                'id': 'wdc04',
                'workerCount': 3
            }
        ]
    }
]


class TestIKSWorkerPool(unittest.TestCase):
    def test_constructor(self):
        worker_pool = IKSWorkerPool(worker_pools_json[0])
        self.assertEqual('bm12clsw08k9uctrq8cg-d423e5a', worker_pool.id)
        self.assertEqual('edge', worker_pool.name)
        self.assertEqual(2, worker_pool.size_per_zone)
        self.assertEqual('public', worker_pool.isolation)
        self.assertEqual(worker_pools_json[0]['labels'], worker_pool.labels)
        self.assertEqual('b2c.4x16.encrypted', worker_pool.machine_type)
        self.assertEqual('us-east', worker_pool.region)
        self.assertEqual('active', worker_pool.state)
        self.assertEqual('', worker_pool.reason_for_delete)
        self.assertEqual(True, worker_pool.is_balanced)
        self.assertEqual(False, worker_pool.autoscale_enabled)
        self.assertEqual(1, len(worker_pool.zones))
        self.assertEqual('wdc04', worker_pool.zones[0].id)

    def test_properties(self):
        worker_pool = IKSWorkerPool(worker_pools_json[0])
        self.assertEqual('bm12clsw08k9uctrq8cg-d423e5a', worker_pool.id)
        worker_pool.id = 'newid'
        self.assertEqual('newid', worker_pool.id)
        worker_pool.name = 'name'
        self.assertEqual('name', worker_pool.name)
        worker_pool.size_per_zone = 3
        self.assertEqual(3, worker_pool.size_per_zone)
        worker_pool.isolation = 'dedicated'
        self.assertEqual('dedicated', worker_pool.isolation)
        labels = {'k1': 'v1'}
        worker_pool.labels = labels
        self.assertEqual(labels, worker_pool.labels)
        worker_pool.labels['k2'] = 'v2'
        self.assertEqual('v1', worker_pool.labels['k1'])
        self.assertEqual('v2', worker_pool.labels['k2'])
        worker_pool.machine_type = 'type'
        self.assertEqual('type', worker_pool.machine_type)
        worker_pool.region = 'region'
        self.assertEqual('region', worker_pool.region)
        worker_pool.state = 'state'
        self.assertEqual('state', worker_pool.state)
        worker_pool.reason_for_delete = 'reason_for_delete'
        self.assertEqual('reason_for_delete', worker_pool.reason_for_delete)
        worker_pool.is_balanced = False
        self.assertEqual(False, worker_pool.is_balanced)
        worker_pool.autoscale_enabled = True
        self.assertEqual(True, worker_pool.autoscale_enabled)
        worker_pool.zones = []
        self.assertEqual([], worker_pool.zones)

    def test_parse_iks_worker_pools(self):
        worker_pools = IKSWorkerPool.parse_iks_worker_pools(worker_pools_json)
        self.assertEqual(2, len(worker_pools))
        self.assertEqual('bm12clsw08k9uctrq8cg-d423e5a', worker_pools[0].id)
        self.assertEqual('bm12clsw08k9uctrq8cg-d7e1428', worker_pools[1].id)


if __name__ == '__main__':
    unittest.main()
