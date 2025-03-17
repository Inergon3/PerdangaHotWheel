from fastapi import HTTPException
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from Crud.crud import valid_count_id, str_list_to_int_list
from model import EventModel, MemberModel, EventMemberModel


class Member:
    def __init__(self, event_obj):
        self.event_obj = event_obj

    async def add(self, member_name, db: AsyncSession):
        try:
            new_member = MemberModel(name=member_name)
            db.add(new_member)
            await db.commit()
        finally:
            await db.close()
        return new_member

    async def get_all(self, db: AsyncSession):
        try:
            stmt = select(MemberModel)
            result = await db.execute(stmt)
            members = result.scalars().all()
        finally:
            await db.close()
        return members

    async def get_for_id_list(self, id_list, db):
        if id_list is not None:
            id_list = await str_list_to_int_list(id_list)
            stmt = select(MemberModel).where(MemberModel.id.in_(id_list))
            result = await db.execute(stmt)
            events = result.scalars().all()
            await valid_count_id(events, id_list)
            return events
        events = await self.get_all(db)
        return events

    async def get_for_id(self, id, db: AsyncSession):
        stmt = (select(MemberModel).where(MemberModel.id == id))
        result = await db.execute(stmt)
        member = result.scalars().first()
        if member == None:
            raise HTTPException(status_code=404, detail=f"Member {id} not found")
        return member

    async def get_participates_events(self, member_id, db: AsyncSession):
        await self.get_for_id(member_id, db)
        subquery = (
            select(
                EventMemberModel.event_id,
                func.count(EventMemberModel.member_id).label('participation_count')
            )
            .join(MemberModel, EventMemberModel.member_id == MemberModel.id)
            .where(MemberModel.id == member_id)
            .group_by(EventMemberModel.event_id)
            .subquery()
        )

        stmt = (
            select(EventModel)
            .join(subquery, EventModel.id == subquery.c.event_id)
            .where(subquery.c.participation_count != 0)
        )
        result = await db.execute(stmt)

        result_all = result.scalars().all()
        return result_all

    async def get_not_participates_events(self, member_id, db: AsyncSession):
        await self.get_for_id(member_id, db)
        subquery = (
            select(
                EventMemberModel.event_id,
                func.count(EventMemberModel.member_id).label('participation_count')
            )
            .join(MemberModel, EventMemberModel.member_id == MemberModel.id)
            .where(MemberModel.id == member_id)
            .group_by(EventMemberModel.event_id)
            .subquery()
        )

        stmt = (
            select(EventModel)
            .join(subquery, EventModel.id == subquery.c.event_id, isouter=True)
            .where((subquery.c.participation_count == 0) | (subquery.c.event_id.is_(None)))
        )

        result = await db.execute(stmt)
        result_all = result.scalars().all()
        return result_all

    async def del_for_id(self, member_id, db: AsyncSession):
        members = await self.get_for_id_list(member_id, db)
        stmt = delete(EventModel).where(EventModel.id.in_(member_id))
        await db.execute(stmt)
        await db.commit()
        return members

    async def add_in_event(self, member_id, event_id, db: AsyncSession):
        await self.get_for_id(member_id, db)
        await self.event_obj.get_for_id(event_id, db)
        event_member = EventMemberModel(event_id=event_id, member_id=member_id)
        db.add(event_member)
        await db.commit()
