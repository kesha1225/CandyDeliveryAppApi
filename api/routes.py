from typing import Type, TypeVar, Callable

from aiohttp import web
from aiohttp.web_request import Request
from pydantic import BaseModel, ValidationError

from api.models import CouriersPostRequest


# TODO: Отдельно описать роутеры и отдельно добавлять и запускать

routes = web.RouteTableDef()


T = TypeVar("T")


def import_couriers_error_handler(json_data: dict, validation_error: ValidationError):
    bad_data = [{"id": json_data["data"][error["loc"][1]]["courier_id"]} for error in validation_error.errors()]
    return bad_data


def get_model_from_json_data(json_data: dict, model: Type[BaseModel], error_handler: Callable):
    print(json_data)
    try:
        deserialized_model = model(**json_data)
    except ValidationError as e:
        return error_handler(json_data, e)

    return deserialized_model

# TODO: вынести ерор хендлеры

@routes.post('/couriers')
async def import_couriers(request: Request):
    data = get_model_from_json_data(await request.json(), model=CouriersPostRequest, error_handler=import_couriers_error_handler)
    print()
    print(data)
    return web.Response(text="Hello, world")


app = web.Application()
app.add_routes(routes)

web.run_app(app)
