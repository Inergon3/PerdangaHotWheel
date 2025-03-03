from fastapi import HTTPException
from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from model import MemberModel, EventModel, GameModel, EventMemberModel


class Event:
    async def add(name, start_event, end_event, db: AsyncSession):
        try:
            new_event = EventModel(name=name, start_event=start_event, end_event=end_event)
            db.add(new_event)
            await db.commit()
        except:
            return "Error"
        finally:
            await db.close()
        return "Event создан"

    async def get_all(db: AsyncSession):
        stmt = select(EventModel)
        result = await db.execute(stmt)
        events = result.scalars().all()
        return events

    async def get_for_name(names, db: AsyncSession):
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
            stmt = select(EventModel).where(EventModel.name.in_(names))
            result = await db.execute(stmt)
            event = result.scalars().first()
            return event
        finally:
            await db.close()

    async def del_for_name(names, db: AsyncSession):
        ob_event = Event
        event = await ob_event.get_for_name(names, db)
        if event == True:
            stmt = delete(EventModel).where(EventModel.name.in_(names))
            await db.execute(stmt)
            await db.commit()
            return f'Events = {names} delited'
        raise HTTPException(status_code=404, detail="Error")


class Member:
    async def add(member_name, db: AsyncSession):
        try:
            new_member = MemberModel(name=member_name)
            db.add(new_member)
            await db.commit()
        finally:
            await db.close()
        return new_member

    async def get_all(db: AsyncSession):
        try:
            stmt = select(MemberModel)
            result = await db.execute(stmt)
            members = result.scalars().all()
        finally:
            await db.close()
        return members

    async def get_for_name(names, db):
        try:
            type_table = "Member"
            if isinstance(names, list):
                member_not_found = []
                for name in names:
                    if await valid_member_name_or_event_name(name, type_table, db) == 0:
                        member_not_found.append(name)
                if member_not_found != []:
                    raise HTTPException(status_code=404, detail=f'Error, Events: {member_not_found} not found')
            stmt = select(MemberModel).where(MemberModel.name.in_(names))
            result = await db.execute(stmt)
            event = result.scalars().first()
            return event
        finally:
            await db.close()

    async def add_in_event(member_name, event_name, db: AsyncSession):
        try:
            type_table = "Event"
            if await valid_member_name_or_event_name(event_name, type_table, db) == 0:
                raise HTTPException(status_code=404, detail=f"Error, event = {event_name} not found")
            type_table = "Member"
            if await valid_member_name_or_event_name(member_name, type_table, db) == 0:
                raise HTTPException(status_code=404, detail=f"Error, member = {member_name} not found")
            stmt = select(MemberModel).filter(MemberModel.name == member_name)
            result = await db.execute(stmt)
            member = result.scalars().first()
            stmt = select(EventModel).filter(EventModel.name == event_name)
            result = await db.execute(stmt)
            event = result.scalars().first()
            rel = EventMemberModel(event_id=event.id, member_id=member.id)
            db.add(rel)
            await db.commit()
        finally:
            await db.close()
        return rel

    async def get_participates_events(name_member, db: AsyncSession):
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

    async def get_not_participates_events(name_member, db: AsyncSession):
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

    async def del_for_name(names, db: AsyncSession):
        ob_member = Member
        member = await ob_member.get_for_name(names, db)
        if member == True:
            stmt = delete(EventModel).where(EventModel.name.in_(names))
            await db.execute(stmt)
            await db.commit()
            return f'Members = {names} delited'
        raise HTTPException(status_code=404, detail="Error")


class Game:
    async def add_for_member(name_game, name_member, event_name, db: AsyncSession):
        try:
            if await valid_game_name_for_event(name_game, event_name, db) != True:
                raise HTTPException(status_code=404,
                                    detail=f"Game с именем = {name_game} в event = {event_name} уже есть")
            if await valid_game_for_member(name_game, name_member, db) != True:
                raise HTTPException(status_code=404, detail=f"Game с именем = {name_game} у {name_member} уже есть")
            stmt = select(MemberModel).filter(MemberModel.name == name_member)
            result = await db.execute(stmt)
            member = result.scalars().first()
            stmt = select(EventModel).filter(EventModel.name == event_name)
            result = await db.execute(stmt)
            event = result.scalars().first()
            new_game = GameModel(name=name_game, user_id=member.id, event_id=event.id)
            db.add(new_game)
            await db.commit()
        finally:
            await db.close()
        return new_game

    async def del_game_for_name_member_name(name, member_name, db: AsyncSession):
        ob_game = Game
        game = await ob_game.get_for_member(name, member_name, db)
        db.delete(game)
        return f"{name} у {member_name} удален"

    async def get_for_member(game_name, member_name, db: AsyncSession):
        if valid_game_for_member(game_name, member_name, db) == False:
            ob_member = Member
            member = ob_member.get_for_name(member_name, db)
            stmt = select(GameModel).where(and_(GameModel.user_id == member.id, GameModel.name == game_name))
            result = await db.execute(stmt)
            game = result.scalars().first()
            return game
        raise HTTPException(status_code=404, detail=f"{game_name} у {member_name} не найден")

    async def get_all(db: AsyncSession):
        stmt = select(GameModel)
        result = await db.execute(stmt)
        games = result.scalars().all()
        if games == []:
            return "Нет игр"
        return games

    async def get_all_from_event(event_name, db: AsyncSession):
        stmt = select(GameModel).where(EventModel.name == event_name)
        result = await db.execute(stmt)
        games = result.scalars().all()
        if games == []:
            return f"В event {event_name} нет игр"
        return games


async def valid_game_name_for_event(name, event_name, db: AsyncSession):
    try:
        ob_event = Event
        event = await ob_event.get_for_name(event_name, db)
        stmt = select(func.count()).select_from(GameModel).where(
            and_(GameModel.name == name, GameModel.event_id == event.id))
        result = await db.execute(stmt)
        result_first = result.scalars().first()
    finally:
        await db.close()
    if result_first != 0:
        return False
    return True


async def valid_member_name_or_event_name(name, type_table, db: AsyncSession):
    if type_table == "Member":
        table = MemberModel
    elif type_table == "Event":
        table = EventModel
    else:
        raise HTTPException(status_code=404, detail="Error, type_table not found")
    stmt = select(func.count()).select_from(table).where(table.name == name)
    result = await db.execute(stmt)
    result_first = result.scalars().first()
    return result_first


async def valid_game_for_member(game_name, member_name, db: AsyncSession):
    try:
        ob_member = Member
        member = await ob_member.get_for_name(member_name, db)
        stmt = select(func.count()).select_from(GameModel).where(
            and_(GameModel.name == game_name, GameModel.user_id == member.id))
        result = await db.execute(stmt)
        result_first = result.scalars().first()
    finally:
        await db.close()
    if result_first != 0:
        return False
    return True
