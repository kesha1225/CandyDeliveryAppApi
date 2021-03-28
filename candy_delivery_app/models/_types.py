from typing import Type, Union

from pydantic import conlist, constr, conint, BaseModel

REGIONS = conlist(conint(strict=True, ge=0))
HOURS_LIST = conlist(constr(strict=True))
ORDER_ID = conint(strict=True, gt=0)
COURIER_ID = conint(strict=True, gt=0)
STATUS_CODE = int
REASON = str
MODEL_DATA = Union[dict, Type[BaseModel], int]
