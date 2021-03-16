from aiohttp import web

from candy_delivery_app.api import couriers_router, orders_router

app = web.Application()
app.add_routes(couriers_router)
app.add_routes(orders_router)
