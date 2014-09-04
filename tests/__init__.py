import unittest

from .test_withings_activity import TestWithingsActivity
from .test_withings_api import TestWithingsApi
from .test_withings_auth import TestWithingsAuth
from .test_withings_credentials import TestWithingsCredentials
from .test_withings_measure_group import TestWithingsMeasureGroup
from .test_withings_measures import TestWithingsMeasures
from .test_withings_object import TestWithingsObject


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWithingsActivity))
    suite.addTest(unittest.makeSuite(TestWithingsApi))
    suite.addTest(unittest.makeSuite(TestWithingsAuth))
    suite.addTest(unittest.makeSuite(TestWithingsCredentials))
    suite.addTest(unittest.makeSuite(TestWithingsMeasureGroup))
    suite.addTest(unittest.makeSuite(TestWithingsMeasures))
    suite.addTest(unittest.makeSuite(TestWithingsObject))
    return suite
