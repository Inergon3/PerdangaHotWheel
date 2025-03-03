import datetime

import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud import Event, Member, Game
from model import SessionLocal
from schemas import NamesSchemas

app = FastAPI()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


event = Event
member = Member
game = Game


@app.post("/event/add/{name}")
async def add_event_in_db(name: str, start_event: datetime.datetime = datetime.datetime.now(),
                          end_event: datetime.datetime = datetime.datetime.now(), db: AsyncSession = Depends(get_db)):
    return await event.add(name, start_event, end_event, db)


@app.get("/event/get/all")
async def get_all_events(db: AsyncSession = Depends(get_db)):
    return await event.get_all(db)


@app.get("/event/get/{name}")
async def get_event(name: str, db: AsyncSession = Depends(get_db)):
    return await event.get_for_name(name, db)


@app.post("/member/add/{name}")
async def add_member_in_db(name: str, db: AsyncSession = Depends(get_db)):
    return await member.add(name, db)


@app.get("/member/get/all")
async def get_all_members(db: AsyncSession = Depends(get_db)):
    return await member.get_all(db)


@app.get("/member/get/{name}")
async def get_member(name: str, db: AsyncSession = Depends(get_db)):
    return await member.get_for_name(name, db)


@app.post("/game/add/{name_event}/{name_member}/{name_game}")
async def add_games_for_members(name_game: str, name_member: str, name_event: str, db: AsyncSession = Depends(get_db)):
    return await game.add_for_member(name_game, name_member, name_event, db)


@app.post("/eventmember/add/{name_event}/{name_member}")
async def add_event_for_member(name_event: str, name_member: str, db: AsyncSession = Depends(get_db)):
    return await member.add_in_event(name_member, name_event, db)


@app.delete("/delete/event/")
async def del_events_from_list_names(name: NamesSchemas, db: AsyncSession = Depends(get_db)):
    return await event.del_for_name(name.names, db)


@app.delete("/delete/member/")
async def del_members_from_list_names(name: NamesSchemas, db: AsyncSession = Depends(get_db)):
    return await member.del_for_name(name.names, db)


@app.delete("/delete/game/{name_member}/{name_game}")
async def del_game_for_member(name_member, name_game, db: AsyncSession = Depends(get_db)):
    return await game.del_game_for_name_member_name(name_game, name_member, db)


@app.get("/get/events/{name_member}")
async def get_events_for_member(name_member: str, db: AsyncSession = Depends(get_db)):
    participates = await member.get_participates_events(name_member, db)
    not_participates = await member.get_not_participates_events(name_member, db)
    return f"Учавсвует:{participates} Не учавствует:{not_participates}"


@app.get("/game/get/all")
async def get_all_game(db: AsyncSession = Depends(get_db)):
    return await ame.get_all(db)


@app.get("/game/get/all/{name_event}")
async def get_all_game_from_event(name_event, db: AsyncSession = Depends(get_db)):
    return await game.get_all_from_event(name_event, db)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
