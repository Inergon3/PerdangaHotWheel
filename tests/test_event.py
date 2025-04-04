import datetime
import unittest

from fastapi import HTTPException

from Crud.objects import event_obj
from model import get_db


class TestEventAdd(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.event = event_obj
        async for db in get_db():
            self.db = db
            break

    # async def asyncTearDown(self):
    #     # Обязательно закрываем генератор!
    #     await self.db_gen.aclose()

    async def test_add(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        result = await self.event.add("test_ok", now, now, self.db)
        self.assertEqual(result.name, "test_ok")

    async def test_add_conflict(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        await self.event.add("dup_event", now, now, self.db)

        with self.assertRaises(HTTPException) as cm:
            await self.event.add("dup_event", now, now, self.db)

        self.assertEqual(cm.exception.status_code, 409)
