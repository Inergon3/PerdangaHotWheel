import random

from fastapi import HTTPException
from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from model import MemberModel, EventModel, GameModel, EventMemberModel


class Event:
    async def add(self, name, start_event, end_event, db: AsyncSession):
        try:
            new_event = EventModel(name=name, start_event=start_event, end_event=end_event)
            db.add(new_event)
            await db.commit()
        except:
            return "Error"
        finally:
            await db.close()
        return "Event создан"

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
            raise HTTPException(status_code=404, detail="Event not found")
        return event

    async def get_for_id_list(self, id: str, db: AsyncSession):
        try:
            id_list_str = id.split(",")
            id_list_int = []
            for id in id_list_str:
                id_list_int.append(int(id))
        except:
            raise HTTPException(status_code=404, detail="Error")
        stmt = select(EventModel).where(EventModel.id.in_(id_list_int))
        result = await db.execute(stmt)
        events = result.scalars().all()
        if len(events) != len(id_list_int):
            found_ids = {event.id for event in events}
            missing_ids = [id for id in id_list_int if id not in found_ids]
            raise HTTPException(status_code=404, detail=f"Events with the following IDs were not found: {missing_ids}")
        return events

    async def del_for_id(self, event_id, db: AsyncSession):
        not_found_id = []
        for id in event_id:
            event = await self.get_for_id(id, db)
            if event == "Event not found":
                not_found_id.append(id)
        if not_found_id == []:
            stmt = delete(EventModel).where(EventModel.id.in_(event_id))
            await db.execute(stmt)
            await db.commit()
            return f'Events = {event.name} delited'
        raise HTTPException(status_code=404, detail=f"Error, {not_found_id} not found")


class Member:
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

    async def get_for_id_list(self, id_list_str, db):
        try:
            id_list_str = id.split(",")
            id_list_int = []
            for id in id_list_str:
                id_list_int.append(int(id))
        except:
            raise HTTPException(status_code=404, detail="Error")
        stmt = select(MemberModel).where(MemberModel.id.in_(id_list_int))
        result = await db.execute(stmt)
        members = result.scalars().all()
        if len(members) != len(id_list_int):
            found_ids = {event.id for event in members}
            missing_ids = [id for id in id_list_int if id not in found_ids]
            raise HTTPException(status_code=404, detail=f"Members with the following IDs were not found: {missing_ids}")
        return members
        # try:
        #     type_table = "Member"
        #     if isinstance(ids, list):
        #         member_not_found = []
        #         for id in ids:
        #             if await valid_member_name_or_event_name(id, type_table, db) == 0:
        #                 member_not_found.append(name)
        #         if member_not_found != []:
        #             raise HTTPException(status_code=404, detail=f'Error, Events: {member_not_found} not found')
        #     stmt = select(MemberModel).where(MemberModel.name.in_(names))
        #     result = await db.execute(stmt)
        #     event = result.scalars().first()
        #     return event
        # finally:
        #     await db.close()
    async def get_for_id(self, id: int, db: AsyncSession):
        stmt = (select(MemberModel).where(MemberModel.id == id))
        result = await db.execute(stmt)
        member = result.scalars().first()
        if member == None:
            raise HTTPException(status_code=404, detail="Member not found")
        return member
    async def add_in_event(self, member_name, event_name, db: AsyncSession):
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

    async def get_participates_events(self, name_member, db: AsyncSession):
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

    async def get_not_participates_events(self, name_member, db: AsyncSession):
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

    async def del_for_name(self, names, db: AsyncSession):
        ob_member = Member
        member = await ob_member.get_for_name(names, db)
        if member == True:
            stmt = delete(EventModel).where(EventModel.name.in_(names))
            await db.execute(stmt)
            await db.commit()
            return f'Members = {names} delited'
        raise HTTPException(status_code=404, detail="Error")

    # async def add_win_game(self, member_name, event_name, db: AsyncSession):
    #     member = self.get_for_name(member_name,db)
    #     game = Game
    #     member.gameWin = await game.get_random_game_from_event(event_name, db)
    #     stmt = (update(EventMemberModel).where(and_(self.name == member_name, self.))


class Game:
    async def add_for_member(self, name_game, name_member, event_id, db: AsyncSession):
        try:
            # if await valid_game_name_for_event(name_game, event_id, db) != True:
            #     raise HTTPException(status_code=404,
            #                         detail=f"Game с именем = {name_game} в event = {event_id} уже есть")
            # if await valid_game_for_member(name_game, name_member, db) != True:
            #     raise HTTPException(status_code=404, detail=f"Game с именем = {name_game} у {name_member} уже есть")
            stmt = select(MemberModel).filter(MemberModel.name == name_member)
            result = await db.execute(stmt)
            member = result.scalars().first()
            stmt = select(EventModel).filter(EventModel.id == event_id)
            result = await db.execute(stmt)
            event = result.scalars().first()
            if member == None:
                raise HTTPException(status_code=404, detail="member not found")
            if event == None:
                raise HTTPException(status_code=404, detail="event not found")
            new_game = GameModel(name=name_game, user_id=member.id, event_id=event.id)
            db.add(new_game)
            await db.commit()
        finally:
            await db.close()
        return new_game

    async def del_game_for_name_member_name(self, name, member_name, db: AsyncSession):
        ob_game = Game
        game = await ob_game.get_for_member(name, member_name, db)
        db.delete(game)
        return f"{name} у {member_name} удален"

    async def get_for_member(self, game_name, member_name, db: AsyncSession):
        if valid_game_for_member(game_name, member_name, db) == False:
            ob_member = Member
            member = ob_member.get_for_name(member_name, db)
            stmt = select(GameModel).where(and_(GameModel.user_id == member.id, GameModel.name == game_name))
            result = await db.execute(stmt)
            game = result.scalars().first()
            return game
        raise HTTPException(status_code=404, detail=f"{game_name} у {member_name} не найден")

    async def get_all(self, db: AsyncSession):
        stmt = select(GameModel)
        result = await db.execute(stmt)
        games = result.scalars().all()
        if games == []:
            return "Нет игр"
        return games

    async def get_all_from_event(self, event_name, db: AsyncSession):
        stmt = select(GameModel).where(EventModel.name == event_name)
        result = await db.execute(stmt)
        games = result.scalars().all()
        if games == []:
            return f"В event {event_name} нет игр"
        return games

    async def get_random_game_from_event(self, member_id, event_id, db: AsyncSession):
        stmt = select(GameModel).where.and_(GameModel.user_id != member_id, GameModel.event_id == event_id)
        result = await db.execute(stmt)
        game_list = result.scalars().all()
        random_game = random.choice(game_list)
        return random_game


async def valid_game_name_for_event(name, event_id, db: AsyncSession):
    try:
        ob_event = Event
        event = await ob_event.get_for_id(event_id, db)
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
