from typing import List, Type, Union

from pydantic.main import BaseModel

REGIONS = List[int]
WORKING_HOURS = List[str]
ORDER_ID = int
COURIER_ID = int
STATUS_CODE = int
REASON = str
MODEL_DATA = Union[dict, Type[BaseModel]]
