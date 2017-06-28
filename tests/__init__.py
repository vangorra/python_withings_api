import unittest

from .test_nokia_activity import TestNokiaActivity
from .test_nokia_api import TestNokiaApi
from .test_nokia_auth import TestNokiaAuth
from .test_nokia_credentials import TestNokiaCredentials
from .test_nokia_measure_group import TestNokiaMeasureGroup
from .test_nokia_measures import TestNokiaMeasures
from .test_nokia_object import TestNokiaObject
from .test_nokia_sleep import TestNokiaSleep
from .test_nokia_sleep_series import TestNokiaSleepSeries


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNokiaActivity))
    suite.addTest(unittest.makeSuite(TestNokiaApi))
    suite.addTest(unittest.makeSuite(TestNokiaAuth))
    suite.addTest(unittest.makeSuite(TestNokiaCredentials))
    suite.addTest(unittest.makeSuite(TestNokiaMeasureGroup))
    suite.addTest(unittest.makeSuite(TestNokiaMeasures))
    suite.addTest(unittest.makeSuite(TestNokiaObject))
    suite.addTest(unittest.makeSuite(TestNokiaSleep))
    suite.addTest(unittest.makeSuite(TestNokiaSleepSeries))
    return suite
