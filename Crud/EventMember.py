from fastapi import HTTPException
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

#from Crud.objects import event_obj, member_obj, game_obj
from model import EventMemberModel


class EventMember:
    def __init__(self, event_obj, member_obj, game_obj):
        self.event_obj = event_obj
        self.member_obj = member_obj
        self.game_obj = game_obj

    async def get_all(self, db: AsyncSession):
        stmt = select(EventMemberModel)
        result = await db.execute(stmt)
        events_members = result.scalars().all()
        if events_members == None:
            raise HTTPException(status_code=404, detail="not found")
        return events_members

    async def get_for_event_id_member_id(self, event_id, member_id, db: AsyncSession):
        await self.event_obj.get_for_id(event_id, db)
        await self.member_obj.get_for_id(member_id, db)
        stmt = select(EventMemberModel).where(
            and_(EventMemberModel.event_id == event_id, EventMemberModel.member_id == member_id))
        result = await db.execute(stmt)
        eventmember = result.scalars().first()
        if eventmember == None:
            raise HTTPException(status_code=404, detail="eventmember not found")
        return eventmember

    async def add_win_game(self, member_id, event_id, db: AsyncSession):
        eventmember = await self.get_for_event_id_member_id(event_id, member_id, db)
        random_game = await self.game_obj.get_random_game_from_event(member_id, event_id, db)
        eventmember.game_win = random_game
        stmt = update(EventMemberModel).where(
            and_(EventMemberModel.member_id == member_id, EventMemberModel.event_id == event_id)).values(
            game_win=random_game)
        await db.execute(stmt)
        await db.commit()
        return random_game


