from aiohttp import web
from aiohttp.web_request import Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..business_models.couriers import CouriersPostRequest
from ..db.db import get_session, update_base
from ..db.models.couriers import Courier

couriers_router = web.RouteTableDef()


@couriers_router.post("/couriers")
@get_session
async def import_couriers(request: Request, session: AsyncSession):
    print((await session.execute("SELECT * FROM couriers")).fetchall())

    json_data = await request.json()
    # TODO: мб что то отдельное для validation_error

    status_code, reason, data = CouriersPostRequest.get_model_from_json_data(
        json_data=json_data
    )
    if status_code == 201:
        couriers = await Courier.create_couriers(session=session, json_data=json_data)
        if couriers is None:  # IntegrityError
            return web.json_response(
                data={"validation_error": data}, status=409, reason="Id Dublicates"
            )
    return web.json_response(data=data, status=status_code, reason=reason)
