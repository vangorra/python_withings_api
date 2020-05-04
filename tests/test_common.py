"""Tests for common code."""
from typing import Any, Dict

import arrow
import pytest
from typing_extensions import Final
from withings_api.common import (
    AuthFailedException,
    BadStateException,
    ErrorOccurredException,
    InvalidParamsException,
    MeasureGetMeasGroup,
    MeasureGetMeasGroupAttrib,
    MeasureGetMeasGroupCategory,
    MeasureGetMeasMeasure,
    MeasureGetMeasResponse,
    MeasureGroupAttribs,
    MeasureType,
    MeasureTypes,
    SleepModel,
    TimeoutException,
    TooManyRequestsException,
    UnauthorizedException,
    UnexpectedTypeException,
    UnknownStatusException,
    enforce_type,
    enum_or_raise,
    get_measure_value,
    query_measure_groups,
    response_body_or_raise,
)
from withings_api.const import (
    STATUS_AUTH_FAILED,
    STATUS_BAD_STATE,
    STATUS_ERROR_OCCURRED,
    STATUS_INVALID_PARAMS,
    STATUS_SUCCESS,
    STATUS_TIMEOUT,
    STATUS_TOO_MANY_REQUESTS,
    STATUS_UNAUTHORIZED,
)

from .common import TIMEZONE0


def test_enforce_type_exception() -> None:
    """Test function."""
    with pytest.raises(Exception):
        enforce_type("blah", int)


def test_enum_or_raise() -> None:
    """Test function."""
    with pytest.raises(Exception):
        enum_or_raise(None, SleepModel)


def test_query_measure_groups() -> None:
    """Test function."""
    response: Final = MeasureGetMeasResponse(
        offset=0,
        more=False,
        timezone=TIMEZONE0,
        updatetime=arrow.get(100000),
        measuregrps=(
            MeasureGetMeasGroup(
                attrib=MeasureGetMeasGroupAttrib.MANUAL_USER_DURING_ACCOUNT_CREATION,
                category=MeasureGetMeasGroupCategory.USER_OBJECTIVES,
                created=arrow.get(10000200),
                date=arrow.get(10000300),
                deviceid="dev1",
                grpid=1,
                measures=(
                    MeasureGetMeasMeasure(type=MeasureType.WEIGHT, unit=1, value=10),
                    MeasureGetMeasMeasure(
                        type=MeasureType.BONE_MASS, unit=-2, value=20
                    ),
                ),
            ),
            MeasureGetMeasGroup(
                attrib=MeasureGetMeasGroupAttrib.MEASURE_USER_CONFIRMED,
                category=MeasureGetMeasGroupCategory.USER_OBJECTIVES,
                created=arrow.get(10000400),
                date=arrow.get(10000500),
                deviceid="dev2",
                grpid=2,
                measures=(
                    MeasureGetMeasMeasure(
                        type=MeasureType.BONE_MASS, unit=21, value=210
                    ),
                    MeasureGetMeasMeasure(
                        type=MeasureType.FAT_FREE_MASS, unit=-22, value=220
                    ),
                ),
            ),
        ),
    )

    # Measure type filter.
    expected1: Final = tuple(
        [
            MeasureGetMeasGroup(
                attrib=MeasureGetMeasGroupAttrib.MANUAL_USER_DURING_ACCOUNT_CREATION,
                category=MeasureGetMeasGroupCategory.USER_OBJECTIVES,
                created=arrow.get(10000200),
                date=arrow.get(10000300),
                deviceid="dev1",
                grpid=1,
                measures=(),
            ),
            MeasureGetMeasGroup(
                attrib=MeasureGetMeasGroupAttrib.MEASURE_USER_CONFIRMED,
                category=MeasureGetMeasGroupCategory.USER_OBJECTIVES,
                created=arrow.get(10000400),
                date=arrow.get(10000500),
                deviceid="dev2",
                grpid=2,
                measures=(
                    MeasureGetMeasMeasure(
                        type=MeasureType.FAT_FREE_MASS, unit=-22, value=220
                    ),
                ),
            ),
        ]
    )
    assert query_measure_groups(response, MeasureType.FAT_FREE_MASS) == expected1

    expected2: Final = tuple(
        [
            MeasureGetMeasGroup(
                attrib=MeasureGetMeasGroupAttrib.MEASURE_USER_CONFIRMED,
                category=MeasureGetMeasGroupCategory.USER_OBJECTIVES,
                created=arrow.get(10000400),
                date=arrow.get(10000500),
                deviceid="dev2",
                grpid=2,
                measures=(
                    MeasureGetMeasMeasure(
                        type=MeasureType.FAT_FREE_MASS, unit=-22, value=220
                    ),
                ),
            )
        ]
    )
    assert (
        query_measure_groups(
            response,
            MeasureType.FAT_FREE_MASS,
            MeasureGetMeasGroupAttrib.MEASURE_USER_CONFIRMED,
        )
        == expected2
    )

    expected3: Final = tuple(
        [
            MeasureGetMeasGroup(
                attrib=MeasureGetMeasGroupAttrib.MANUAL_USER_DURING_ACCOUNT_CREATION,
                category=MeasureGetMeasGroupCategory.USER_OBJECTIVES,
                created=arrow.get(10000200),
                date=arrow.get(10000300),
                deviceid="dev1",
                grpid=1,
                measures=(
                    MeasureGetMeasMeasure(
                        type=MeasureType.BONE_MASS, unit=-2, value=20
                    ),
                ),
            ),
            MeasureGetMeasGroup(
                attrib=MeasureGetMeasGroupAttrib.MEASURE_USER_CONFIRMED,
                category=MeasureGetMeasGroupCategory.USER_OBJECTIVES,
                created=arrow.get(10000400),
                date=arrow.get(10000500),
                deviceid="dev2",
                grpid=2,
                measures=(
                    MeasureGetMeasMeasure(
                        type=MeasureType.BONE_MASS, unit=21, value=210
                    ),
                ),
            ),
        ]
    )
    assert query_measure_groups(response, MeasureType.BONE_MASS) == expected3

    # Group attrib filter.
    assert query_measure_groups(response) == response.measuregrps

    assert (
        query_measure_groups(response, MeasureTypes.ANY, MeasureGroupAttribs.ANY)
        == response.measuregrps
    )

    assert query_measure_groups(
        response, MeasureTypes.ANY, MeasureGroupAttribs.AMBIGUOUS
    ) == (response.measuregrps[0],)

    assert query_measure_groups(
        response, MeasureTypes.ANY, MeasureGroupAttribs.UNAMBIGUOUS
    ) == (response.measuregrps[1],)

    assert query_measure_groups(
        response, MeasureTypes.ANY, response.measuregrps[0].attrib
    ) == (response.measuregrps[0],)


def test_get_measure_value() -> None:
    """Test function."""
    response: Final = MeasureGetMeasResponse(
        offset=0,
        more=False,
        timezone=TIMEZONE0,
        updatetime=arrow.get(100000),
        measuregrps=(
            MeasureGetMeasGroup(
                attrib=MeasureGetMeasGroupAttrib.MANUAL_USER_DURING_ACCOUNT_CREATION,
                category=MeasureGetMeasGroupCategory.USER_OBJECTIVES,
                created=arrow.utcnow(),
                date=arrow.utcnow(),
                deviceid="dev1",
                grpid=1,
                measures=(
                    MeasureGetMeasMeasure(type=MeasureType.WEIGHT, unit=1, value=10),
                    MeasureGetMeasMeasure(
                        type=MeasureType.BONE_MASS, unit=-2, value=20
                    ),
                ),
            ),
        ),
    )

    assert get_measure_value(response, MeasureType.BODY_TEMPERATURE) is None

    assert get_measure_value(response.measuregrps, MeasureType.BODY_TEMPERATURE) is None

    assert (
        get_measure_value(response.measuregrps[0], MeasureType.BODY_TEMPERATURE) is None
    )

    assert get_measure_value(response, MeasureType.WEIGHT) == 100
    assert get_measure_value(response.measuregrps, MeasureType.WEIGHT) == 100
    assert get_measure_value(response.measuregrps[0], MeasureType.WEIGHT) == 100

    assert get_measure_value(response, MeasureType.BONE_MASS) == 0.2
    assert get_measure_value(response.measuregrps, MeasureType.BONE_MASS) == 0.2
    assert get_measure_value(response.measuregrps[0], MeasureType.BONE_MASS) == 0.2


def response_status_factory(status: Any) -> Dict[str, Any]:
    """Return mock response."""
    return {"status": status, "body": {}}


def test_response_body_or_raise() -> None:
    """Test function."""
    with pytest.raises(UnexpectedTypeException):
        response_body_or_raise("hello")

    with pytest.raises(UnknownStatusException):
        response_body_or_raise(response_status_factory("hello"))

    for status in STATUS_SUCCESS:
        response_body_or_raise(response_status_factory(status))

    for status in STATUS_AUTH_FAILED:
        with pytest.raises(AuthFailedException):
            response_body_or_raise(response_status_factory(status))

    for status in STATUS_INVALID_PARAMS:
        with pytest.raises(InvalidParamsException):
            response_body_or_raise(response_status_factory(status))

    for status in STATUS_UNAUTHORIZED:
        with pytest.raises(UnauthorizedException):
            response_body_or_raise(response_status_factory(status))

    for status in STATUS_ERROR_OCCURRED:
        with pytest.raises(ErrorOccurredException):
            response_body_or_raise(response_status_factory(status))

    for status in STATUS_TIMEOUT:
        with pytest.raises(TimeoutException):
            response_body_or_raise(response_status_factory(status))

    for status in STATUS_BAD_STATE:
        with pytest.raises(BadStateException):
            response_body_or_raise(response_status_factory(status))

    for status in STATUS_TOO_MANY_REQUESTS:
        with pytest.raises(TooManyRequestsException):
            response_body_or_raise(response_status_factory(status))

    with pytest.raises(UnknownStatusException):
        response_body_or_raise(response_status_factory(100000))
