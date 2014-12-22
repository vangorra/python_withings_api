import time
import unittest

from withings import WithingsMeasureGroup


class TestWithingsMeasureGroup(unittest.TestCase):
    def test_attributes(self):
        """
        Check that attributes get set as expected when creating a
        WithingsMeasureGroup object
        """
        data = {
            'attrib': 2,
            'measures': [
                {'unit': -1, 'type': 1, 'value': 860}
            ],
            'date': 1409361740,
            'category': 1,
            'grpid': 111111111
        }
        group = WithingsMeasureGroup(data)
        self.assertEqual(group.data, data)
        self.assertEqual(group.grpid, data['grpid'])
        self.assertEqual(group.attrib, data['attrib'])
        self.assertEqual(group.category, data['category'])
        self.assertEqual(group.date.timestamp, 1409361740)
        self.assertEqual(group.measures, data['measures'])
        for _type, type_id in WithingsMeasureGroup.MEASURE_TYPES:
            assert hasattr(group, _type)
            self.assertEqual(getattr(group, _type),
                             86.0 if _type == 'weight' else None)

    def test_types(self):
        """
        Check that all the different measure types are working as expected
        """
        for _, type_id in WithingsMeasureGroup.MEASURE_TYPES:
            data = {
                'attrib': 2,
                'measures': [
                    {'unit': -1, 'type': type_id, 'value': 860}
                ],
                'date': 1409361740,
                'category': 1,
                'grpid': 111111111
            }
            group = WithingsMeasureGroup(data)
            for _type, type_id2 in WithingsMeasureGroup.MEASURE_TYPES:
                assert hasattr(group, _type)
                self.assertEqual(getattr(group, _type),
                                 86.0 if type_id == type_id2 else None)

    def test_multigroup_types(self):
        """
        Check that measure typse with multiple measurements in the group are
        working as expected
        """
        data = {
            'attrib': 2,
            'measures': [
                {'unit': -1, 'type': 9, 'value': 800},
                {'unit': -1, 'type': 10, 'value': 1200},
                {'unit': -1, 'type': 11, 'value': 860}
            ],
            'date': 1409361740,
            'category': 1,
            'grpid': 111111111
        }
        group = WithingsMeasureGroup(data)
        for _type, type_id in WithingsMeasureGroup.MEASURE_TYPES:
            assert hasattr(group, _type)
            if _type == 'diastolic_blood_pressure':
                self.assertEqual(getattr(group, _type), 80.0)
            elif _type == 'systolic_blood_pressure':
                self.assertEqual(getattr(group, _type), 120.0)
            elif _type == 'heart_pulse':
                self.assertEqual(getattr(group, _type), 86.0)
            else:
                self.assertEqual(getattr(group, _type), None)

    def test_is_ambiguous(self):
        """ Test the is_ambiguous method """
        data = {'attrib': 0, 'measures': [], 'date': 1409361740, 'category': 1,
                'grpid': 111111111}
        self.assertEqual(WithingsMeasureGroup(data).is_ambiguous(), False)
        data['attrib'] = 1
        assert WithingsMeasureGroup(data).is_ambiguous()
        data['attrib'] = 2
        self.assertEqual(WithingsMeasureGroup(data).is_ambiguous(), False)
        data['attrib'] = 4
        assert WithingsMeasureGroup(data).is_ambiguous()

    def test_is_measure(self):
        """ Test the is_measure method """
        data = {'attrib': 0, 'measures': [], 'date': 1409361740, 'category': 1,
                'grpid': 111111111}
        assert WithingsMeasureGroup(data).is_measure()
        data['category'] = 2
        self.assertEqual(WithingsMeasureGroup(data).is_measure(), False)

    def test_is_target(self):
        """ Test the is_target method """
        data = {'attrib': 0, 'measures': [], 'date': 1409361740, 'category': 1,
                'grpid': 111111111}
        self.assertEqual(WithingsMeasureGroup(data).is_target(), False)
        data['category'] = 2
        assert WithingsMeasureGroup(data).is_target()

    def test_get_measure(self):
        """
        Check that the get_measure function is working as expected
        """
        data = {
            'attrib': 2,
            'measures': [
                {'unit': -2, 'type': 9, 'value': 8000},
                {'unit': 1, 'type': 10, 'value': 12},
                {'unit': 0, 'type': 11, 'value': 86}
            ],
            'date': 1409361740,
            'category': 1,
            'grpid': 111111111
        }
        group = WithingsMeasureGroup(data)
        self.assertEqual(group.get_measure(9), 80.0)
        self.assertEqual(group.get_measure(10), 120.0)
        self.assertEqual(group.get_measure(11), 86.0)
        self.assertEqual(group.get_measure(12), None)
