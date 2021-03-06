from typing import Type, TypeVar, Tuple, Union

from aiohttp import web
from aiohttp.web_request import Request

from api.models import CouriersPostRequest

# TODO: Отдельно описать роутеры и отдельно добавлять и запускать

routes = web.RouteTableDef()


@routes.post("/couriers")
async def import_couriers(request: Request):
    status_code, reason, data = CouriersPostRequest.get_model_from_json_data(
        json_data=await request.json()
    )
    return web.json_response(data=data, status=status_code, reason=reason)


app = web.Application()
app.add_routes(routes)

web.run_app(app)
