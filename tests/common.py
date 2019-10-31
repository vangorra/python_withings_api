"""Common test code."""
from datetime import tzinfo
from typing import cast

from dateutil import tz

TIMEZONE_STR0 = "Europe/London"
TIMEZONE_STR1 = "America/Los_Angeles"
TIMEZONE0 = cast(tzinfo, tz.gettz(TIMEZONE_STR0))
TIMEZONE1 = cast(tzinfo, tz.gettz(TIMEZONE_STR1))
