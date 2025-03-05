from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud import Game
from model import get_db

router = APIRouter(prefix="/game", tags=["games"])
game = Game()


@router.post("/add/{name_event}/{name_member}/{name_game}")
async def add_games_for_members(name_game: str, name_member: str, event_id: int, db: AsyncSession = Depends(get_db)):
    return await game.add_for_member(name_game, name_member, event_id, db)


@router.delete("/delete/{name_member}/{name_game}")
async def del_game_for_member(name_member, name_game, db: AsyncSession = Depends(get_db)):
    return await game.del_game_for_name_member_name(name_game, name_member, db)


@router.get("/get/all")
async def get_all_game(db: AsyncSession = Depends(get_db)):
    return await game.get_all(db)


@router.get("/get/all/{name_event}")
async def get_all_game_from_event(name_event, db: AsyncSession = Depends(get_db)):
    return await game.get_all_from_event(name_event, db)


@router.get("/get/random/member_id={member_id}, event_id={event_id}/")
async def get_random_game(member_id: int, event_id: int, db: AsyncSession = Depends(get_db)):
    return await game.get_random_game_from_event(member_id, event_id, db)
