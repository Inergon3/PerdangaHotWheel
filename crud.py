from fastapi import HTTPException
from sqlalchemy import select, func, and_, delete
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


async def get_member_for_name(names, db):
    try:
        type_table = "Member"
        if isinstance(names, list):
            member_not_found = []
            for name in names:
                if await valid_member_name_or_event_name(name, type_table, db) == 0:
                    member_not_found.append(name)
            if member_not_found != []:
                raise HTTPException(status_code=404, detail=f'Error, Events: {member_not_found} not found')
        result = await db.execute(select(MemberModel).where(MemberModel.name.in_(names)))
        event = result.scalars().first()
        return event
    finally:
        await db.close()


async def add_games_for_member(name_game, name_member, event_name, db: AsyncSession):
    try:
        if await value_game_name_for_event(name_game, event_name, db) != True:
            raise HTTPException(status_code=404, detail=f"Game с именем = {name_game} в event = {event_name} уже есть")
        if await valid_game_for_member(name_game, name_member, db) != True:
            raise HTTPException(status_code=404, detail=f"Game с именем = {name_game} у {name_member} уже есть")
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


async def value_game_name_for_event(name, event_name, db: AsyncSession):
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


async def get_event_for_name(names, db: AsyncSession):
    try:
        type_table = "Event"
        if isinstance(names, list):
            event_not_found = []
            for name in names:
                if await valid_member_name_or_event_name(name, type_table, db) == 0:
                    event_not_found.append(name)
            if event_not_found != []:
                raise HTTPException(status_code=404, detail=f'Error, Events: {event_not_found} not found')
            return True
        result = await db.execute(select(EventModel).where(EventModel.name.in_(names)))
        event = result.scalars().first()
        return event
    finally:
        await db.close()


async def add_member_in_event(member_name, event_name, db: AsyncSession):
    try:
        type_table = "Event"
        if await valid_member_name_or_event_name(event_name, type_table, db) == 0:
            raise HTTPException(status_code=404, detail=f"Error, event = {event_name} not found")
        type_table = "Member"
        if await valid_member_name_or_event_name(member_name, type_table, db) == 0:
            raise HTTPException(status_code=404, detail=f"Error, member = {member_name} not found")
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
    result = await db.execute(select(func.count()).select_from(table).where(table.name == name))
    result_first = result.scalars().first()
    return result_first


async def get_event_for_member_participates(name_member, db: AsyncSession):
    type_table = "Member"
    if await valid_member_name_or_event_name(name_member, type_table, db) == 0:
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
    type_table = "Member"
    if await valid_member_name_or_event_name(name_member, type_table, db) == 0:
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


async def del_members_for_name(names, db: AsyncSession):
    member = await get_member_for_name(names, db)
    if member == True:
        stmt = delete(EventModel).where(EventModel.name.in_(names))
        await db.execute(stmt)
        await db.commit()
        return f'Members = {names} delited'
    raise HTTPException(status_code=404, detail="Error")


async def del_events_for_name(names, db: AsyncSession):
    event = await get_event_for_name(names, db)
    if event == True:
        stmt = delete(EventModel).where(EventModel.name.in_(names))
        await db.execute(stmt)
        await db.commit()
        return f'Events = {names} delited'
    raise HTTPException(status_code=404, detail="Error")

async def valid_game_for_member(game_name, member_name, db: AsyncSession):
    try:
        member = await get_member_for_name(member_name, db)
        result = await db.execute(select(func.count()).select_from(GameModel).where(
            and_(GameModel.name == game_name, GameModel.user_id == member.id)))
        result_first = result.scalars().first()
    finally:
        await db.close()
    if result_first != 0:
        return False
    return True
async def del_game_for_name_member_name(name, member_name, db:AsyncSession):
    game = await get_game_for_member(name, member_name, db)
    db.delete(game)
    return f"{name} у {member_name} удален"

async def get_game_for_member(game_name, member_name, db:AsyncSession):
    if valid_game_for_member(game_name, member_name, db) == False:
        member = get_member_for_name(member_name,db)
        stmt = select(GameModel).where(and_(GameModel.user_id == member.id, GameModel.name == game_name))
        result = await db.execute(stmt)
        game = result.scalars().first()
        return game
    raise HTTPException(status_code=404, detail=f"{game_name} у {member_name} не найден")

async def get_all_games(db:AsyncSession):
    stmt = select(GameModel)
    result = await db.execute(stmt)
    games = result.scalars().all()
    if games == []:
        return "Нет игр"
    return games

async def get_all_games_for_event(event_name,db:AsyncSession):
    stmt = select(GameModel).where(EventModel.name == event_name)
    result = await db.execute(stmt)
    games = result.scalars().all()
    if games == []:
        return f"В event {event_name} нет игр"
    return games