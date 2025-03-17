from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

#from Crud.Game import Game
from Crud.objects import game_obj
from model import get_db
from schemas import GameSchemas

router = APIRouter(prefix="/games", tags=["games"])



@router.post("/add")
async def add_games_for_members(added_game: GameSchemas, db: AsyncSession = Depends(get_db)):
    await game_obj.add_for_member(added_game.game_name, added_game.member_id, added_game.event_id, db)
    return


@router.delete("/delete")
async def del_game_for_member(added_game: GameSchemas, db: AsyncSession = Depends(get_db)):
    await game_obj.del_game_for_name_member_name(added_game.game_name, added_game.member_id, added_game.event_id, db)
    return


@router.get("/get/all")
async def get_all_game(db: AsyncSession = Depends(get_db)):
    result = await game_obj.get_all(db)
    return {
        "data": result
    }


@router.get("/get/all/{event_id}")
async def get_all_game_from_event(event_id: int, db: AsyncSession = Depends(get_db)):
    result = await game_obj.get_all_from_event(event_id, db)
    return {
        "data": result
    }


@router.get("/get/random/")
async def get_random_game(member_id: int, event_id: int, db: AsyncSession = Depends(get_db)):
    result = await game_obj.get_random_game_from_event(member_id, event_id, db)
    return {
        "data": result
    }
