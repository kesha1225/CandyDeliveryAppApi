from functools import lru_cache


def get_best_orders(raw_orders, capacity: int):
    @lru_cache(maxsize=None)
    def best_weight(items_number, weight_limit):
        if items_number == 0:
            return items_number
        elif raw_orders[items_number - 1].weight > weight_limit:
            return best_weight(items_number - 1, weight_limit)
        return max(
            best_weight(items_number - 1, weight_limit),
            best_weight(
                items_number - 1, weight_limit - raw_orders[items_number - 1].weight
            )
            + raw_orders[items_number - 1].weight,
        )

    result = []
    for i in reversed(range(len(raw_orders))):
        if best_weight(i + 1, capacity) > best_weight(i, capacity):
            result.append(raw_orders[i])
            capacity -= raw_orders[i].weight

    return result
