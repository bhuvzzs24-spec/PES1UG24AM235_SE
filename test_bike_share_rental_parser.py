"""Property-based fuzz tests for all three Lab 7 parser functions."""

from hypothesis import example, given, strategies as st
from bike_share_rental_parser import (
    parse_ride_duration,
    format_station_code,
    parse_ride_log,
)


@example(None)
@example("")
@example("01:75")
@example("01:15")
@given(st.text() | st.none())
def test_parse_ride_duration_no_crash(s):
    try:
        result = parse_ride_duration(s)
    except Exception as exc:
        raise AssertionError(f"parse_ride_duration crashed for {s!r}") from exc
    assert isinstance(result, int)
    assert result >= 0
    if s == "01:15":
        assert result == 75


@example(None)
@example("")
@example("a12")
@example(" A-12 ")
@given(st.text() | st.none())
def test_format_station_code_no_crash(s):
    try:
        result = format_station_code(s)
    except Exception as exc:
        raise AssertionError(f"format_station_code crashed for {s!r}") from exc
    assert isinstance(result, str)
    if s in ("a12", " A-12 "):
        assert result == "A-12"


@example(None)
@example("")
@example("electric,45,yes")
@example("electric,not_a_number,yes")
@given(st.text() | st.none())
def test_parse_ride_log_no_crash(s):
    try:
        result = parse_ride_log(s)
    except Exception as exc:
        raise AssertionError(f"parse_ride_log crashed for {s!r}") from exc
    assert isinstance(result, tuple) and len(result) == 3
    assert isinstance(result[0], str)
    assert isinstance(result[1], int) and result[1] >= 0
    assert isinstance(result[2], bool)
    if s == "electric,45,yes":
        assert result == ("electric", 45, True)
