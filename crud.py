import random

from fastapi import HTTPException
from sqlalchemy import select, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from model import EventModel, MemberModel, EventMemberModel, GameModel


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
            raise HTTPException(status_code=404, detail="Event not found")
        return event

    async def get_for_id_list(self, id_list, db: AsyncSession):
        print(id_list)
        print(type(id_list))
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


#
#
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

    async def get_for_id_list(self, id_list, db):
        id_list = await str_list_to_int_list(id_list)
        stmt = select(MemberModel).where(MemberModel.id.in_(id_list))
        result = await db.execute(stmt)
        events = result.scalars().all()
        await valid_count_id(events, id_list)
        return events

    async def get_for_id(self, id, db: AsyncSession):
        stmt = (select(MemberModel).where(MemberModel.id == id))
        result = await db.execute(stmt)
        member = result.scalars().first()
        if member == None:
            raise HTTPException(status_code=404, detail="Member not found")
        return member

    async def add_in_event(self, member_id, event_id, db: AsyncSession):
        ob_event = Event()
        await self.get_for_id(member_id, db)
        await ob_event.get_for_id(event_id, db)
        event_member = EventMemberModel(event_id=event_id, member_id=member_id)
        db.add(event_member)
        await db.commit()

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

    # async def add_win_game(self, member_name, event_name, db: AsyncSession):
    #     member = self.get_for_name(member_name,db)
    #     game = Game
    #     member.gameWin = await game.get_random_game_from_event(event_name, db)
    #     stmt = (update(EventMemberModel).where(and_(self.name == member_name, self.))


#
#
class Game:
    pass

    async def add_for_member(self, name_game, member_id, event_id, db: AsyncSession):
        try:

            ob_member = Member()
            member = await ob_member.get_for_id(member_id, db)
            ob_event = Event()
            event = await ob_event.get_for_id(event_id, db)
            await self.check_for_game_in_event(name_game, event_id, db)
            await self.check_for_game_in_memebr(name_game, member_id, db)

            new_game = GameModel(name=name_game, user_id=member.id, event_id=event.id)
            db.add(new_game)
            await db.commit()
        finally:
            await db.close()
        return new_game

    async def check_for_game_in_event(self, game_name, event_id, db: AsyncSession):
        stmt = select(GameModel).where(and_(GameModel.name == game_name, GameModel.event_id == event_id))
        result = await db.execute(stmt)
        game = result.scalars().first()
        if game != None:
            raise HTTPException(status_code=404, detail="Игра в этом event уже есть")
        return True

    async def check_for_game_in_memebr(self, game_name, member_id, db: AsyncSession):
        stmt = select(GameModel).where(and_(GameModel.name == game_name, GameModel.user_id == member_id))
        result = await db.execute(stmt)
        game = result.scalars().first()
        if game != None:
            raise HTTPException(status_code=404, detail="У этого member уже есть эта game")
        return True

    async def del_game_for_name_member_name(self, game_name, member_id, event_id, db: AsyncSession):
        game = await self.get_for_member(game_name, member_id, event_id, db)
        db.delete(game)
        return game

    async def get_for_member(self, game_name, member_id, event_id, db: AsyncSession):
        ob_member = Member()
        member = await ob_member.get_for_id(member_id, db)
        stmt = select(GameModel).where(
            and_(GameModel.user_id == member.id, GameModel.name == game_name, GameModel.id == event_id))
        result = await db.execute(stmt)
        game = result.scalars().first()
        if game == None:
            raise HTTPException(status_code=404, detail="Game not found")
        return game

    async def get_all(self, db: AsyncSession):
        stmt = select(GameModel)
        result = await db.execute(stmt)
        games = result.scalars().all()
        if games == []:
            raise HTTPException(status_code=404, detail="Нет игр")
        return games

    async def get_all_from_event(self, event_id, db: AsyncSession):
        stmt = select(GameModel).where(EventModel.id == event_id)
        result = await db.execute(stmt)
        games = result.scalars().all()
        if games == []:
            raise HTTPException(status_code=404, detail="В event нет игр")
        return games

    async def get_random_game_from_event(self, member_id, event_id, db: AsyncSession):
        stmt = select(GameModel).where.and_(GameModel.user_id != member_id, GameModel.event_id == event_id)
        result = await db.execute(stmt)
        game_list = result.scalars().all()
        random_game = random.choice(game_list)
        return random_game


class EventMember:
    async def get_all(self, db: AsyncSession):
        stmt = select(EventMemberModel)
        result = await db.execute(stmt)
        events_members = result.scalars().all()
        if events_members == None:
            raise HTTPException(status_code=404, detail="not found")
        return events_members


async def valid_count_id(id_list1, id_list2):
    if len(id_list1) != len(id_list2):
        found_ids = {event.id for event in id_list1}
        missing_ids = [id for id in id_list2 if id not in found_ids]
        raise HTTPException(status_code=404, detail={
            "message": "Object with the following IDs were not found:",
            "not found object": missing_ids
        })


async def str_list_to_int_list(id_list):
    if isinstance(id_list, str):
        id_list_str = id_list.split(",")
        id_list = []
        for id in id_list_str:
            id_list.append(int(id))
    return id_list
