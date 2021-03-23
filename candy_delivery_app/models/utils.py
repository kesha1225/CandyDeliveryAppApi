import datetime
import re
from typing import List, Dict

from candy_delivery_app.models import HOURS_LIST


period_re = re.compile(r"^(\d\d):(\d\d)-(\d\d):(\d\d)$")


def get_hours_and_minutes_from_str(raw_date: str):
    period = re.findall(period_re, raw_date)
    if not period:
        raise ValueError(f"Invalid date - {raw_date}")

    first_hour, first_minute, second_hour, second_minute = map(int, period[0])
    return first_hour, first_minute, second_hour, second_minute


def hours_validate(value: HOURS_LIST):
    for raw_period in value:
        (
            first_hour,
            first_minute,
            second_hour,
            second_minute,
        ) = get_hours_and_minutes_from_str(raw_period)

        if any(filter(lambda hour: hour > 23, [first_hour, second_hour])) or any(
            filter(lambda minute: minute > 59, [first_minute, second_minute])
        ):
            raise ValueError(f"Invalid date - {raw_period}")

    return value


def get_timedeltas_from_string(value: HOURS_LIST) -> List[Dict[str, int]]:
    new_values = []
    for raw_period in value:
        (
            first_hour,
            first_minute,
            second_hour,
            second_minute,
        ) = get_hours_and_minutes_from_str(raw_period)

        first_time = datetime.timedelta(hours=first_hour, minutes=first_minute)
        second_time = datetime.timedelta(hours=second_hour, minutes=second_minute)
        new_values.append(
            {
                "first_time": int(first_time.total_seconds()),
                "second_time": int(second_time.total_seconds()),
            }
        )
    return new_values
