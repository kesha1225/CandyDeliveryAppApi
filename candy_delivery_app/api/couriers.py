from aiohttp import web
from aiohttp.web_request import Request


from ..business_models.couriers import CouriersPostRequest

couriers_router = web.RouteTableDef()


@couriers_router.post("/couriers")
async def import_couriers(request: Request):
    status_code, reason, data = CouriersPostRequest.get_model_from_json_data(json_data=await request.json())
    return web.json_response(data=data, status=status_code, reason=reason)
