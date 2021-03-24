from typing import Type, Union

from pydantic import conlist, constr, conint
from pydantic.main import BaseModel

REGIONS = conlist(conint(strict=True, ge=0), min_items=1)
HOURS_LIST = conlist(constr(strict=True), min_items=1)
ORDER_ID = conint(strict=True, gt=0)
COURIER_ID = conint(strict=True, gt=0)
STATUS_CODE = int
REASON = str
MODEL_DATA = Union[dict, Type[BaseModel], int]
