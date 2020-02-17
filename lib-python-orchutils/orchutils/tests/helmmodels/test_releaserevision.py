import datetime
import unittest

from orchutils.helmmodels.releaserevision import ReleaseRevision

revisions_json = [
    {
        'revision': 1,
        'updated': 'Thu Mar 28 10:17:32 2019',
        'status': 'SUPERSEDED',
        'chart': 'p2paas-console-namespace-1.20190327.14',
        'description': 'Install complete'
    },
    {
        'revision': 2,
        'updated': 'Fri Apr 19 13:15:31 2019',
        'status': 'SUPERSEDED',
        'chart': 'p2paas-console-namespace-1.20190419.7',
        'description': 'Upgrade complete'
    },
    {
        'revision': 3,
        'updated': 'Fri Apr 19 13:31:22 2019',
        'status': 'DEPLOYED',
        'chart': 'p2paas-console-namespace-1.20190419.8',
        'description': 'Upgrade complete'
    }
]


class TestReleaseRevision(unittest.TestCase):
    def test_constructor(self):
        rev = revisions_json[0]
        revision = ReleaseRevision(rev)
        self.assertEqual(rev['chart'], revision.chart)
        self.assertEqual(rev['description'], revision.description)
        self.assertEqual(rev['revision'], revision.revision)
        self.assertEqual(rev['status'], revision.status)
        self.assertEqual(datetime.datetime.strptime(rev['updated'], '%a %b %d %H:%M:%S %Y'), revision.updated)

    def test_properties(self):
        revision = ReleaseRevision(revisions_json[0])
        self.assertEqual(revisions_json[0]['chart'], revision.chart)
        revision.chart = 'chart'
        self.assertEqual('chart', revision.chart)
        revision.description = 'description'
        self.assertEqual('description', revision.description)
        revision.revision = 20
        self.assertEqual(20, revision.revision)
        revision.status = 'status'
        self.assertEqual('status', revision.status)
        str_time = 'Wed Mar 27 10:00:00 2019'
        revision.updated = str_time
        self.assertEqual(datetime.datetime.strptime(str_time, '%a %b %d %H:%M:%S %Y'), revision.updated)
        obj_time = datetime.datetime.now()
        revision.updated = obj_time
        self.assertEqual(obj_time, revision.updated)

    def test_parse_ReleaseRevision(self):
        revisions = ReleaseRevision.parse_release_revisions(revisions_json)
        self.assertEqual(3, len(revisions))
        self.assertEqual(revisions_json[0]['chart'], revisions[0].chart)
        self.assertEqual(revisions_json[2]['chart'], revisions[2].chart)


if __name__ == '__main__':
    unittest.main()
