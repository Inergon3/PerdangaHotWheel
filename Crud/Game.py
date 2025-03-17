import random

from fastapi import HTTPException
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

# from Crud.objects import member_obj, event_obj
from model import EventModel, GameModel


class Game:
    def __init__(self, event_obj, member_obj):
        self.event_obj = event_obj
        self.member_obj = member_obj

    async def add_for_member(self, name_game, member_id, event_id, db: AsyncSession):
        member = await self.member_obj.get_for_id(member_id, db)
        event = await self.event_obj.get_for_id(event_id, db)
        await self.check_for_game_in_event(name_game, event_id, db)
        await self.check_for_game_in_memebr(name_game, member_id, db)
        new_game = GameModel(name=name_game, user_id=member.id, event_id=event.id)
        db.add(new_game)
        await db.commit()
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
        await self.get_for_member(game_name, member_id, event_id, db)
        stmt = delete(GameModel).where(
            and_(GameModel.user_id == member_id, GameModel.name == game_name, GameModel.event_id == event_id))
        await db.execute(stmt)
        await db.commit()
        return

    async def get_for_member(self, game_name, member_id, event_id, db: AsyncSession):
        member = await self.member_obj.get_for_id(member_id, db)
        stmt = select(GameModel).where(
            and_(GameModel.user_id == member.id, GameModel.name == game_name, GameModel.event_id == event_id))
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
        stmt = select(GameModel).where(and_(GameModel.user_id != member_id, GameModel.event_id == event_id))
        result = await db.execute(stmt)
        game_list = result.scalars().all()
        random_game = random.choice(game_list)
        return random_game.name
