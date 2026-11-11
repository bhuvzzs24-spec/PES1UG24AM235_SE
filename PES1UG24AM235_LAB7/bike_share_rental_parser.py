"""Lab 7 - robust parsing of bike-share rental input.

Malformed input uses safe defaults instead of raising:
  - duration: 0 minutes
  - station code: empty string
  - ride log: ('', 0, False)
"""

import re


def parse_ride_duration(text):
    """Convert a valid HH:MM duration to minutes; otherwise return 0.

    Hours may have any number of digits; minutes must have exactly two
    digits in the range 00-59. Negative durations are not supported.
    """
    if not isinstance(text, str):
        return 0
    match = re.fullmatch(r"([0-9]+):([0-9]{2})", text.strip())
    if match is None:
        return 0
    try:
        hours = int(match.group(1))
        minutes = int(match.group(2))
    except ValueError:
        return 0
    if minutes >= 60:
        return 0
    return hours * 60 + minutes


def format_station_code(code):
    """Format a letter-plus-number station code as ZONE-NUMBER.

    Invalid or missing codes return an empty string. Already-formatted
    codes are accepted as well (e.g. 'A-12').
    """
    if not isinstance(code, str):
        return ""
    cleaned = code.strip().upper()
    match = re.fullmatch(r"([A-Z])-?([0-9]+)", cleaned)
    if match is None:
        return ""
    return f"{match.group(1)}-{match.group(2)}"


def parse_ride_log(line):
    """Parse 'bike_type,minutes,subscriber' into (str, int, bool).

    Only nonnegative whole-minute counts and 'yes' or 'no' subscriber
    flags are accepted; invalid lines return ('', 0, False).
    """
    default = ("", 0, False)
    if not isinstance(line, str):
        return default
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 3:
        return default
    bike_type, minutes_text, subscriber = parts
    if not bike_type or subscriber.lower() not in ("yes", "no"):
        return default
    if re.fullmatch(r"[0-9]+", minutes_text) is None:
        return default
    try:
        minutes = int(minutes_text)
    except ValueError:
        return default
    return bike_type, minutes, subscriber.lower() == "yes"


def main():
    print("==== Running parse_ride_duration ====")
    value = input("Enter a ride duration as HH:MM (e.g. 01:15): ")
    print("Duration in minutes:", parse_ride_duration(value))

    print("\n==== Running format_station_code ====")
    value = input("Enter a station code (e.g. a12): ")
    print("Formatted station code:", format_station_code(value))

    print("\n==== Running parse_ride_log ====")
    value = input("Enter a ride log line as type,minutes,subscriber (e.g. electric,45,yes): ")
    print("Parsed ride log:", parse_ride_log(value))


if __name__ == "__main__":
    main()
