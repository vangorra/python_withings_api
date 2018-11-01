import time
import unittest

from datetime import timedelta
from nokia import NokiaSleepSummarySeries


class TestNokiaSleepSummarySeries(unittest.TestCase):
    def test_attributes(self):
        data = {
            'data':  {
                'deepsleepduration': 18660,
                'durationtosleep': 0,
                'durationtowakeup': 240,
                'lightsleepduration': 20220,
                'wakeupcount': 1,
                'wakeupduration': 720,
            },
            'date': '2018-10-30',
            'enddate': 1540897020,
            'id': 900363515,
            'model': 16,
            'modified': 1540897246,
            'startdate': 1540857420,
            'timezone': 'Europe/London',
        }
        flat_data = {
            'deepsleepduration': 18660,
            'durationtosleep': 0,
            'durationtowakeup': 240,
            'lightsleepduration': 20220,
            'wakeupcount': 1,
            'wakeupduration': 720,
            'date': '2018-10-30',
            'enddate': 1540897020,
            'id': 900363515,
            'model': 16,
            'modified': 1540897246,
            'startdate': 1540857420,
            'timezone': 'Europe/London',
        }

        series = NokiaSleepSummarySeries(data)
        self.assertEqual(type(series), NokiaSleepSummarySeries)
        self.assertEqual(series.startdate.timestamp, flat_data['startdate'])
        self.assertEqual(series.data, flat_data)
        self.assertEqual(series.enddate.timestamp, flat_data['enddate'])
        self.assertEqual(series.timedelta, timedelta(seconds=39600))
