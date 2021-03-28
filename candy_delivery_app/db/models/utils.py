from typing import Dict


def check_courier_can_delivery_by_time(
    order_timedelta: Dict[str, int], courier_timedelta: Dict[str, int]
):
    order_first_time, order_second_time = (
        order_timedelta["first_time"],
        order_timedelta["second_time"],
    )
    courier_first_time, courier_second_time = (
        courier_timedelta["first_time"],
        courier_timedelta["second_time"],
    )

    # if (
    #     courier_first_time <= order_first_time < courier_second_time
    #     or courier_first_time < order_second_time <= courier_second_time
    # ):

    latest_start = max(order_first_time, courier_first_time)
    earliest_end = min(order_second_time, courier_second_time)
    if latest_start < earliest_end:
        return True
    # if (
    #     (
    #         order_first_time < courier_first_time < order_second_time
    #         or order_first_time < courier_second_time < order_second_time
    #     )
    #     or (
    #         courier_first_time < order_first_time < courier_second_time
    #         or courier_first_time < order_second_time < courier_second_time
    #     )
    #     or (
    #         order_first_time == courier_first_time
    #         and order_second_time == courier_second_time
    #     )
    # ):
    #     return True

    return False
