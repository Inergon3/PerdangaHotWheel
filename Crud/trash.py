import asyncio
import datetime

from Crud.objects import event_obj
from model import get_db

event = event_obj


async def test():
    async for db in get_db():
        result = await event.add("test1", datetime.datetime.now(), datetime.datetime.now(), db)
        print(f"result = {result}")


asyncio.run(test())
