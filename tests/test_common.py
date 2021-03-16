"""Tests for common code."""
from typing import Any, Dict

import arrow
import pytest
from typing_extensions import Final
from withings_api.common import (
    ArrowType,
    AuthFailedException,
    BadStateException,
    Credentials,
    Credentials2,
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
    TimeoutException,
    TimeZone,
    TooManyRequestsException,
    UnauthorizedException,
    UnexpectedTypeException,
    UnknownStatusException,
    get_measure_value,
    maybe_upgrade_credentials,
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

from .common import TIMEZONE0, TIMEZONE_STR0


def test_time_zone_validate() -> None:
    """Test TimeZone conversation."""
    with pytest.raises(TypeError):
        assert TimeZone.validate(123)
    with pytest.raises(ValueError):
        assert TimeZone.validate("NOT_A_TIMEZONE")
    assert TimeZone.validate(TIMEZONE_STR0) == TIMEZONE0


def test_arrow_type_validate() -> None:
    """Test ArrowType conversation."""
    with pytest.raises(TypeError):
        assert ArrowType.validate(1.23)

    arrow_obj: Final = arrow.get(1234567)
    assert ArrowType.validate("1234567") == arrow_obj
    assert ArrowType.validate(str(arrow_obj)) == arrow_obj
    assert ArrowType.validate(1234567) == arrow_obj
    assert ArrowType.validate(arrow_obj) == arrow_obj


def test_maybe_update_credentials() -> None:
    """Test upgrade credentials objects."""

    creds1: Final = Credentials(
        access_token="my_access_token",
        token_expiry=arrow.get("2020-01-01T00:00:00+07:00").int_timestamp,
        token_type="Bearer",
        refresh_token="my_refresh_token",
        userid=1,
        client_id="CLIENT_ID",
        consumer_secret="CONSUMER_SECRET",
    )

    expires_in = creds1.token_expiry - arrow.utcnow().int_timestamp
    creds2: Final = Credentials2(
        access_token="my_access_token",
        expires_in=expires_in,
        token_type="Bearer",
        refresh_token="my_refresh_token",
        userid=1,
        client_id="CLIENT_ID",
        consumer_secret="CONSUMER_SECRET",
    )

    assert maybe_upgrade_credentials(creds2) == creds2

    upgraded_creds: Final = maybe_upgrade_credentials(creds1)
    assert upgraded_creds.access_token == creds1.access_token
    assert upgraded_creds.expires_in == expires_in  # pylint: disable=no-member
    assert upgraded_creds.token_type == creds1.token_type
    assert upgraded_creds.refresh_token == creds1.refresh_token
    assert upgraded_creds.userid == creds1.userid
    assert upgraded_creds.client_id == creds1.client_id
    assert upgraded_creds.consumer_secret == creds1.consumer_secret
    assert upgraded_creds.created.format("YYYY-MM-DD HH:mm:ss") == arrow.get(
        creds1.token_expiry - expires_in
    ).format("YYYY-MM-DD HH:mm:ss")
    assert upgraded_creds.token_expiry == creds1.token_expiry


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

    with pytest.raises(UnknownStatusException):
        response_body_or_raise(response_status_factory(None))

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
