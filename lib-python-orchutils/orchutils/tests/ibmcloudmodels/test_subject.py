import json
import unittest

from orchutils.ibmcloudmodels.subject import Subject

subjects_json = [
    {
        'attributes': [
            {
                'name': 'iam_id',
                'value': 'iam-ServiceId-75ae2724-48be-433f-8c83-be05e32e4b60'
            }
        ]
    }
]


class TestSubject(unittest.TestCase):
    def test_constructor(self):
        subject = Subject(subjects_json[0])
        self.assertEqual(1, len(subject.attributes))
        self.assertEqual('iam_id', subject.attributes[0].name)
        self.assertEqual('iam-ServiceId-75ae2724-48be-433f-8c83-be05e32e4b60', subject.attributes[0].value)

    def test_properties(self):
        subject = Subject(subjects_json[0])
        self.assertEqual('iam_id', subject.attributes[0].name)
        subject.attributes = []
        self.assertEqual([], subject.attributes)

    def test_parse_subjects(self):
        subjects = Subject.parse_subjects(subjects_json)
        self.assertEqual(1, len(subjects))
        self.assertEqual('iam_id', subjects[0].attributes[0].name)

    def test_to_json(self):
        subject = Subject(subjects_json[0])
        self.assertEqual(json.dumps(subjects_json[0]), json.dumps(subject, default=lambda o: getattr(o, 'to_json')()))


if __name__ == '__main__':
    unittest.main()
