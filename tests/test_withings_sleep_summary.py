import time
import unittest

from withings_api import WithingsSleepSummary, WithingsSleepSummarySeries


class TestWithingsSleepSummary(unittest.TestCase):
    def test_attributes(self):
        data = {
            'more': False,
            'series': [
                {
                    'data': {
                        'deepsleepduration': 18660,
                        'durationtosleep': 0,
                        'durationtowakeup': 240,
                        'lightsleepduration': 20220,
                        'wakeupcount': 1,
                        'wakeupduration': 720
                    },
                    'date': '2018-10-30',
                    'enddate': 1540897020,
                    'id': 900363515,
                    'model': 16,
                    'modified': 1540897246,
                    'startdate': 1540857420,
                    'timezone': 'Europe/London'
                },
                {
                    'data': {
                        'deepsleepduration': 17040,
                        'durationtosleep': 360,
                        'durationtowakeup': 0,
                        'lightsleepduration': 10860,
                        'wakeupcount': 1,
                        'wakeupduration': 540
                    },
                    'date': '2018-10-31',
                    'enddate': 1540973400,
                    'id': 901269807,
                    'model': 16,
                    'modified': 1541020749,
                    'startdate': 1540944960,
                    'timezone': 'Europe/London'
                }
            ]
        }
        sleep = WithingsSleepSummary(data)
        self.assertEqual(sleep.series[0].model, data['series'][0]['model'])
        self.assertEqual(type(sleep.series), list)
        self.assertEqual(len(sleep.series), 2)
        self.assertEqual(type(sleep.series[0]), WithingsSleepSummarySeries)
        self.assertEqual(sleep.series[0].startdate.timestamp,
                         data['series'][0]['startdate'])
        self.assertEqual(sleep.series[0].enddate.timestamp,
                         data['series'][0]['enddate'])
