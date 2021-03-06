from typing import List

from pydantic import ValidationError


def check_is_regions_positive(value: List[int]):
    if min(value) < 0:
        raise ValidationError("one of region id less than 0")
