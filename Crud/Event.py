from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from Crud.crud import valid_count_id, str_list_to_int_list
from model import EventModel


class Event:
    async def add(self, name, start_event, end_event, db: AsyncSession, user):
        new_event = EventModel(name=name, start_event=start_event, end_event=end_event)
        db.add(new_event)
        await db.commit()
        return new_event

    async def get_all(self, db: AsyncSession):
        stmt = select(EventModel)
        result = await db.execute(stmt)
        events = result.scalars().all()
        return events

    async def get_for_id(self, id: int, db: AsyncSession):
        stmt = (select(EventModel).where(EventModel.id == id))
        result = await db.execute(stmt)
        event = result.scalars().first()
        if event == None:
            raise HTTPException(status_code=404, detail=f"Event {id} not found")
        return event

    async def get_for_id_list(self, id_list, db: AsyncSession):
        if id_list is not None:
            id_list = await str_list_to_int_list(id_list)
            stmt = select(EventModel).where(EventModel.id.in_(id_list))
            result = await db.execute(stmt)
            events = result.scalars().all()
            await valid_count_id(events, id_list)
            return events
        events = await self.get_all(db)
        return events

    async def del_for_id(self, event_id, db: AsyncSession):
        events = await self.get_for_id_list(event_id, db)
        stmt = delete(EventModel).where(EventModel.id.in_(event_id))
        await db.execute(stmt)
        await db.commit()
        return events
