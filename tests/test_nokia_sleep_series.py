import time
import unittest

from datetime import timedelta
from nokia import NokiaSleepSeries


class TestNokiaSleepSeries(unittest.TestCase):
    def test_attributes(self):
        data = {
            "startdate": 1387243618,
            "state": 3,
            "enddate": 1387265218
        }
        series = NokiaSleepSeries(data)
        self.assertEqual(type(series), NokiaSleepSeries)
        self.assertEqual(series.startdate.timestamp, data['startdate'])
        self.assertEqual(series.state, data['state'])
        self.assertEqual(series.enddate.timestamp, data['enddate'])
        self.assertEqual(series.timedelta, timedelta(seconds=21600))
