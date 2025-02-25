import datetime

import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud import add_event, get_all_event, add_member, get_all_member, get_event_for_name, add_member_in_event, \
    add_games_for_member, get_member_for_name, get_event_for_member_participates, get_event_for_member_not_participates, \
    del_events_for_name, del_members_for_name
from model import SessionLocal
from schemas import NamesDelSchemas

app = FastAPI()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@app.post("/event/add/{name}")
async def add_event_in_db(name: str, start_event: datetime.datetime = datetime.datetime.now(),
                          end_event: datetime.datetime = datetime.datetime.now(), db: AsyncSession = Depends(get_db)):
    return await add_event(name, start_event, end_event, db)


@app.get("/event/get/all")
async def get_all_events(db: AsyncSession = Depends(get_db)):
    return await get_all_event(db)


@app.get("/event/get/{name}")
async def get_event(name: str, db: AsyncSession = Depends(get_db)):
    return await get_event_for_name(name, db)


@app.post("/member/add/{name}")
async def add_member_in_db(name: str, db: AsyncSession = Depends(get_db)):
    return await add_member(name, db)


@app.get("/member/get/all")
async def get_all_members(db: AsyncSession = Depends(get_db)):
    return await get_all_member(db)


@app.get("/member/get/{name}")
async def get_member(name: str, db: AsyncSession = Depends(get_db)):
    return await get_member_for_name(name, db)


@app.post("/game/add/{name_event}/{name_member}/{name_game}")
async def add_games_for_members(name_game: str, name_member: str, name_event: str, db: AsyncSession = Depends(get_db)):
    return await add_games_for_member(name_game, name_member, name_event, db)


@app.post("/eventmember/add/{name_event}/{name_member}")
async def add_event_member(name_event: str, name_member: str, db: AsyncSession = Depends(get_db)):
    return await add_member_in_event(name_member, name_event, db)


@app.delete("/delete/event/")
async def del_events_for_list_names(name: NamesDelSchemas, db: AsyncSession = Depends(get_db)):
    return await del_events_for_name(name.names, db)


@app.delete("/delete/member/")
async def del_members_for_list_names(name: NamesDelSchemas, db: AsyncSession = Depends(get_db)):
    return await del_members_for_name(name.names, db)


# """""""""""""" @app.delete("/delete/game/{name_member}/{name_game}")
# """""""""""""" def del_game_for_member(name_member, name_game, db: AsyncSession = Depends(get_db)):
# """"""""""""""     return


@app.get("/get/events/{name_member}")
async def get_events_for_member(name_member: str, db: AsyncSession = Depends(get_db)):
    participates = await get_event_for_member_participates(name_member, db)
    not_participates = await get_event_for_member_not_participates(name_member, db)
    return f"Учавсвует:{participates} Не учавствует:{not_participates}"


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
