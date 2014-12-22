import time
import unittest

from datetime import datetime
from withings import WithingsObject


class TestWithingsObject(unittest.TestCase):
    def test_attributes(self):
        data = {
           "date": "2013-04-10",
           "string": "FAKE_STRING",
           "integer": 55555,
           "float": 5.67
        }
        obj = WithingsObject(data)
        self.assertEqual(obj.date.date().isoformat(), data['date'])
        self.assertEqual(obj.string, data['string'])
        self.assertEqual(obj.integer, data['integer'])
        self.assertEqual(obj.float, data['float'])

        # Test time as epoch
        data = {"date": 1409596058}
        obj = WithingsObject(data)
        self.assertEqual(obj.date.timestamp, data['date'])

        # Test funky time
        data = {"date": "weird and wacky date format"}
        obj = WithingsObject(data)
        self.assertEqual(obj.date, data['date'])
