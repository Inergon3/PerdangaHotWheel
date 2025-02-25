from fastapi import HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from model import MemberModel, EventModel, GameModel, EventMemberModel


async def add_event(name, start_event, end_event, db: AsyncSession):
    try:
        new_event = EventModel(name=name, start_event=start_event, end_event=end_event)
        db.add(new_event)
        await db.commit()
    except:
        return "Error"
    finally:
        await db.close()
    return "Event создан"


async def get_all_event(db: AsyncSession):
    result = await db.execute(select(EventModel))
    events = result.scalars().all()
    return events


async def add_member(member_name, db: AsyncSession):
    try:
        new_member = MemberModel(name=member_name)
        db.add(new_member)
        await db.commit()
        # add_rel_member_event(member_name, event_name, db)
    finally:
        await db.close()
    return new_member


async def get_all_member(db: AsyncSession):
    try:
        result = await db.execute(select(MemberModel))
        members = result.scalars().all()
    finally:
        await db.close()
    return members


async def get_member_for_name(name, db):
    try:
        if await valid_member_name_or_event_name(name_member, type_table="Member", db) == 0:
            raise HTTPException(status_code=404, detail=f'Error, name = {name_member} not found')
        result = await db.execute(select(MemberModel).where(MemberModel.name != name))
        event = result.scalars().first()
    finally:
        await db.close()
    return event


async def add_games_for_member(name_game, name_member, event_name, db: AsyncSession):
    try:
        if await value_game_name(name_game, event_name, db) != True:
            raise HTTPException(status_code=404, detail="Game с таким именем в этом event уже есть")
        result = await db.execute(select(MemberModel).filter(MemberModel.name == name_member))
        member = result.scalars().first()
        result = await db.execute(select(EventModel).filter(EventModel.name == event_name))
        event = result.scalars().first()
        new_game = GameModel(name=name_game, user_id=member.id, event_id=event.id)
        db.add(new_game)
        await db.commit()
    finally:
        await db.close()
    return new_game


#
# async def value_event_name(name, db: AsyncSession):
#     try:
#         result = db.execute(select(func.count()).select_from(EventModel).where(EventModel.name == name))
#     finally:
#         await db.close()
#     if result != 0:
#         return False
#     return True
#
#
# async def value_member_name(name, db: AsyncSession):
#     try:
#         result = db.execute(select(func.count()).select_from(MemberModel).where(MemberModel.name == name))
#     finally:
#         await db.close()
#     if result != 0:
#         return False
#     return True
#

async def value_game_name(name, event_name, db: AsyncSession):
    try:
        event = await get_event_for_name(event_name, db)
        result = await db.execute(select(func.count()).select_from(GameModel).where(
            and_(GameModel.name == name, GameModel.event_id == event.id)))
        result_first = result.scalars().first()
    finally:
        await db.close()
    if result_first != 0:
        return False
    return True


async def get_event_for_name(name, db: AsyncSession):
    try:
        if await valid_member_name_or_event_name(name_member, type_table="Event", db) == 0:
            raise HTTPException(status_code=404, detail=f'Error, Event = {name_member} not found')
        result = await db.execute(select(EventModel).where(EventModel.name == name))
        event = result.scalars().first()
    finally:
        await db.close()
    return event


async def add_member_in_event(member_name, event_name, db: AsyncSession):
    try:
        type_table = "Event"
        if await valid_member_name_or_event_name(event_name, type_table, db) == 0:
            raise HTTPException(status_code=404, detail="Error, event not found")
        type_table = "Member"
        if await valid_member_name_or_event_name(member_name, type_table, db) == 0:
            raise HTTPException(status_code=404, detail="Error, member not found")
        result = await db.execute(select(MemberModel).filter(MemberModel.name == member_name))
        member = result.scalars().first()
        result = await db.execute(select(EventModel).filter(EventModel.name == event_name))
        event = result.scalars().first()
        rel = EventMemberModel(event_id=event.id, member_id=member.id)
        db.add(rel)
        await db.commit()
    finally:
        await db.close()
    return rel


async def valid_member_name_or_event_name(name, type_table, db: AsyncSession):
    if type_table == "Member":
        table = MemberModel
    elif type_table == "Event":
        table = EventModel
    else:
        raise HTTPException(status_code=404, detail="Error, type_table not found")
    result = await db.execute(select(func.count()).select_from(table).filter(table.name == name))
    result_first = result.scalars().first()
    return result_first


async def get_event_for_member_participates(name_member, db: AsyncSession):
    if await valid_member_name_or_event_name(name_member, type_table="Member", db) == 0:
        raise HTTPException(status_code=404, detail=f'Error, name = {name_member} not found')
    subquery = (
        select(
            EventMemberModel.event_id,
            func.count(EventMemberModel.member_id).label('participation_count')
        )
        .join(MemberModel, EventMemberModel.member_id == MemberModel.id)
        .where(MemberModel.name == name_member)
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


async def get_event_for_member_not_participates(name_member, db: AsyncSession):
    if await valid_member_name_or_event_name(name_member, type_table="Member", db) == 0:
        raise HTTPException(status_code=404, detail=f'Error, name = {name_member} not found')
    subquery = (
        select(
            EventMemberModel.event_id,
            func.count(EventMemberModel.member_id).label('participation_count')
        )
        .join(MemberModel, EventMemberModel.member_id == MemberModel.id)
        .where(MemberModel.name == name_member)
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

# async def delite_event(name, db:AsyncSession)
