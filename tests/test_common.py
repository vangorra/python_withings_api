from dateutil import tz

import arrow
import pytest

from withings_api.common import (
    GetMeasResponse,
    GetMeasGroup,
    GetMeasMeasure,
    MeasureType,
    MeasureTypes,
    MeasureGroupAttrib,
    MeasureGroupAttribs,
    MeasureCategory,
    get_measure_value,
    query_measure_groups,
    enforce_type,
    enum_or_raise,
    SleepModel,
)


def test_enforce_type_exception():
    with pytest.raises(Exception):
        enforce_type('blah', int)


def test_enum_or_raise():
    with pytest.raises(Exception):
        enum_or_raise(None, SleepModel)


def test_query_measure_groups():
    response = GetMeasResponse(
        offset=0,
        more=False,
        timezone=tz.gettz('Europe/London'),
        updatetime=arrow.get(100000),
        measuregrps=(
            GetMeasGroup(
                attrib=MeasureGroupAttrib.MANUAL_USER_DURING_ACCOUNT_CREATION,
                category=MeasureCategory.USER_OBJECTIVES,
                created=arrow.get(10000200),
                date=arrow.get(10000300),
                deviceid='dev1',
                grpid='1',
                measures=(
                    GetMeasMeasure(
                        type=MeasureType.WEIGHT,
                        unit=1,
                        value=10,
                    ),
                    GetMeasMeasure(
                        type=MeasureType.BONE_MASS,
                        unit=-2,
                        value=20,
                    ),
                ),
            ),
            GetMeasGroup(
                attrib=MeasureGroupAttrib.MEASURE_USER_CONFIRMED,
                category=MeasureCategory.USER_OBJECTIVES,
                created=arrow.get(10000400),
                date=arrow.get(10000500),
                deviceid='dev2',
                grpid='2',
                measures=(
                    GetMeasMeasure(
                        type=MeasureType.BONE_MASS,
                        unit=21,
                        value=210,
                    ),
                    GetMeasMeasure(
                        type=MeasureType.FAT_FREE_MASS,
                        unit=-22,
                        value=220,
                    ),
                ),
            ),
        ),
    )

    # Measure type filter.
    expected = tuple([
        GetMeasGroup(
            attrib=MeasureGroupAttrib.MANUAL_USER_DURING_ACCOUNT_CREATION,
            category=MeasureCategory.USER_OBJECTIVES,
            created=arrow.get(10000200),
            date=arrow.get(10000300),
            deviceid='dev1',
            grpid='1',
            measures=(),
        ),
        GetMeasGroup(
            attrib=MeasureGroupAttrib.MEASURE_USER_CONFIRMED,
            category=MeasureCategory.USER_OBJECTIVES,
            created=arrow.get(10000400),
            date=arrow.get(10000500),
            deviceid='dev2',
            grpid='2',
            measures=(
                GetMeasMeasure(
                    type=MeasureType.FAT_FREE_MASS,
                    unit=-22,
                    value=220,
                ),
            ),
        ),
    ])
    assert query_measure_groups(
        response,
        MeasureType.FAT_FREE_MASS,
    ) == expected

    expected = tuple([
        GetMeasGroup(
            attrib=MeasureGroupAttrib.MEASURE_USER_CONFIRMED,
            category=MeasureCategory.USER_OBJECTIVES,
            created=arrow.get(10000400),
            date=arrow.get(10000500),
            deviceid='dev2',
            grpid='2',
            measures=(
                GetMeasMeasure(
                    type=MeasureType.FAT_FREE_MASS,
                    unit=-22,
                    value=220,
                ),
            ),
        ),
    ])
    assert query_measure_groups(
        response,
        MeasureType.FAT_FREE_MASS,
        MeasureGroupAttrib.MEASURE_USER_CONFIRMED
    ) == expected

    expected = tuple([
        GetMeasGroup(
            attrib=MeasureGroupAttrib.MANUAL_USER_DURING_ACCOUNT_CREATION,
            category=MeasureCategory.USER_OBJECTIVES,
            created=arrow.get(10000200),
            date=arrow.get(10000300),
            deviceid='dev1',
            grpid='1',
            measures=(
                GetMeasMeasure(
                    type=MeasureType.BONE_MASS,
                    unit=-2,
                    value=20,
                ),
            ),
        ),
        GetMeasGroup(
            attrib=MeasureGroupAttrib.MEASURE_USER_CONFIRMED,
            category=MeasureCategory.USER_OBJECTIVES,
            created=arrow.get(10000400),
            date=arrow.get(10000500),
            deviceid='dev2',
            grpid='2',
            measures=(
                GetMeasMeasure(
                    type=MeasureType.BONE_MASS,
                    unit=21,
                    value=210,
                ),
            ),
        ),
    ])
    assert query_measure_groups(
        response,
        MeasureType.BONE_MASS,
    ) == expected

    # Group attrib filter.
    assert query_measure_groups(response) == response.measuregrps

    assert query_measure_groups(
        response,
        MeasureTypes.ANY,
        MeasureGroupAttribs.ANY
    ) == response.measuregrps

    assert query_measure_groups(
        response,
        MeasureTypes.ANY,
        MeasureGroupAttribs.AMBIGUOUS
    ) == (response.measuregrps[0],)

    assert query_measure_groups(
        response,
        MeasureTypes.ANY,
        MeasureGroupAttribs.UNAMBIGUOUS
    ) == (response.measuregrps[1],)

    assert query_measure_groups(
        response,
        MeasureTypes.ANY,
        response.measuregrps[0].attrib
    ) == (response.measuregrps[0],)


def test_get_measure_value():
    response = GetMeasResponse(
        offset=0,
        more=False,
        timezone=tz.gettz('Europe/London'),
        updatetime=arrow.get(100000),
        measuregrps=(
            GetMeasGroup(
                attrib=MeasureGroupAttrib.MANUAL_USER_DURING_ACCOUNT_CREATION,
                category=MeasureCategory.USER_OBJECTIVES,
                created=arrow.utcnow(),
                date=arrow.utcnow(),
                deviceid='dev1',
                grpid='1',
                measures=(
                    GetMeasMeasure(
                        type=MeasureType.WEIGHT,
                        unit=1,
                        value=10,
                    ),
                    GetMeasMeasure(
                        type=MeasureType.BONE_MASS,
                        unit=-2,
                        value=20,
                    ),
                ),
            ),
        ),
    )

    assert get_measure_value(
        response,
        MeasureType.BODY_TEMPERATURE
    ) is None

    assert get_measure_value(
        response.measuregrps,
        MeasureType.BODY_TEMPERATURE
    ) is None

    assert get_measure_value(
        response.measuregrps[0],
        MeasureType.BODY_TEMPERATURE
    ) is None

    assert get_measure_value(response, MeasureType.WEIGHT) == 100
    assert get_measure_value(response.measuregrps, MeasureType.WEIGHT) == 100
    assert get_measure_value(
        response.measuregrps[0],
        MeasureType.WEIGHT
    ) == 100

    assert get_measure_value(response, MeasureType.BONE_MASS) == 0.2
    assert get_measure_value(
        response.measuregrps,
        MeasureType.BONE_MASS
    ) == 0.2
    assert get_measure_value(
        response.measuregrps[0],
        MeasureType.BONE_MASS
    ) == 0.2
