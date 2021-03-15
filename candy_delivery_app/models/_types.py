from typing import List, Type, Union

from pydantic import conlist, constr
from pydantic.main import BaseModel

REGIONS = List[int]
HOURS_LIST = conlist(constr(strict=True), min_items=1)
ORDER_ID = int
COURIER_ID = int
STATUS_CODE = int
REASON = str
MODEL_DATA = Union[dict, Type[BaseModel]]
