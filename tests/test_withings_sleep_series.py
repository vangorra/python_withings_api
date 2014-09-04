import time
import unittest

from datetime import timedelta
from withings import WithingsSleepSeries


class TestWithingsSleepSeries(unittest.TestCase):
    def test_attributes(self):
        data = {
            "startdate": 1387243618,
            "state": 3,
            "enddate": 1387265218
        }
        series = WithingsSleepSeries(data)
        self.assertEqual(type(series), WithingsSleepSeries)
        self.assertEqual(time.mktime(series.startdate.timetuple()),
                         data['startdate'])
        self.assertEqual(series.state, data['state'])
        self.assertEqual(time.mktime(series.enddate.timetuple()),
                         data['enddate'])
        self.assertEqual(series.timedelta, timedelta(seconds=21600))
