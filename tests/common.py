"""Common test code."""
from datetime import tzinfo
from dateutil import tz
from typing import cast

TIMEZONE_STR0 = 'Europe/London'
TIMEZONE_STR1 = 'America/Los_Angeles'
TIMEZONE0 = cast(tzinfo, tz.gettz(TIMEZONE_STR0))
TIMEZONE1 = cast(tzinfo, tz.gettz(TIMEZONE_STR1))
