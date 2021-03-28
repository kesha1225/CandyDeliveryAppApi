import asyncio

from candy_delivery_app.db.db import update_base
from candy_delivery_app.db.models.orders import Order
from candy_delivery_app.db.models.couriers import Courier

asyncio.get_event_loop().run_until_complete(update_base())
