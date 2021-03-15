import datetime
import re

from candy_delivery_app.models import HOURS_LIST


period_re = re.compile(r"^(\d\d):(\d\d)-(\d\d):(\d\d)$")


def hours_validate(_, value: HOURS_LIST):
    # TODO: не забыть дописать его
    for raw_period in value:
        period = re.findall(period_re, raw_period)
        if not period:
            raise ValueError(f"Invalid date - {raw_period}")

        first_hour, first_minute, second_hour, second_minute = map(int, period[0])

        if any(filter(lambda hour: hour > 23, [first_hour, second_hour])) or any(
            filter(lambda minute: minute > 59, [first_minute, second_minute])
        ):
            raise ValueError(f"Invalid date - {raw_period}")
        print(first_hour, first_minute, second_hour, second_minute)
