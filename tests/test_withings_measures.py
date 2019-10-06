import unittest

from withings_api import WithingsMeasureGroup, WithingsMeasures


class TestWithingsMeasures(unittest.TestCase):
    def test_withings_measures_init(self):
        """
        Check that WithingsMeasures create groups correctly and that the
        update time is parsed correctly
        """
        data = {
            'updatetime': 1409596058,
            'measuregrps': [
                {'attrib': 2, 'date': 1409361740, 'category': 1,
                 'measures': [{'unit': -1, 'type': 1, 'value': 860}],
                 'grpid': 111111111},
                {'attrib': 2, 'date': 1409361740, 'category': 1,
                 'measures': [{'unit': -2, 'type': 4, 'value': 185}],
                 'grpid': 111111112}
            ]
        }
        measures = WithingsMeasures(data)
        self.assertEqual(type(measures), WithingsMeasures)
        self.assertEqual(measures.data, data)
        self.assertEqual(type(measures.measuregrps), list)
        self.assertEqual(len(measures.measuregrps), 2)
        self.assertEqual(measures.measuregrps[0], data['measuregrps'][0])
        self.assertEqual(measures.measuregrps[1], data['measuregrps'][1])
        self.assertEqual(len(measures), 2)
        self.assertEqual(type(measures[0]), WithingsMeasureGroup)
        self.assertEqual(measures[0].weight, 86.0)
        self.assertEqual(measures[1].height, 1.85)
        self.assertEqual(measures.updatetime.timestamp, 1409596058)
