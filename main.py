from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud import add_event, get_all_event, add_member, get_all_member, add_game_player
from model import SessionLocal

app = FastAPI()

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@app.post("/addEvent")
async def add_event_in_db(name: str, db: AsyncSession = Depends(get_db)):
    return await add_event(name, db)

@app.get("/getEvents")
async def get_all_events(db: AsyncSession = Depends(get_db)):
    return await get_all_event(db)

@app.post("/addMember")
async def add_member_in_db(name: str, db: AsyncSession = Depends(get_db)):
    return await add_member(name, db)

@app.get("/getMembers")
async def get_all_members(db: AsyncSession = Depends(get_db)):
    return await get_all_member(db)

@app.get("/addGame")
async def add_game_for_member(name_game: str, id_member: int, db: AsyncSession = Depends(get_db)):
    return await add_game_player(name_game, id_member, db)