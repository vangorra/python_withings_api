import arrow
import unittest

from datetime import datetime
from nokia import NokiaActivity


class TestNokiaActivity(unittest.TestCase):
    def test_attributes(self):
        data = {
           "date": "2013-04-10",
           "steps": 6523,
           "distance": 4600,
           "calories": 408.52,
           "elevation": 18.2,
           "soft": 5880,
           "moderate": 1080,
           "intense": 540,
           "timezone": "Europe/Berlin"
        }
        act = NokiaActivity(data)
        self.assertEqual(act.date.date().isoformat(), data['date'])
        self.assertEqual(act.steps, data['steps'])
        self.assertEqual(act.distance, data['distance'])
        self.assertEqual(act.calories, data['calories'])
        self.assertEqual(act.elevation, data['elevation'])
        self.assertEqual(act.soft, data['soft'])
        self.assertEqual(act.moderate, data['moderate'])
        self.assertEqual(act.intense, data['intense'])
        self.assertEqual(act.timezone, data['timezone'])
