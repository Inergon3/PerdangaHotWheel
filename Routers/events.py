import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from crud import Event
from model import get_db
from schemas import IdSchemas

router = APIRouter(prefix="/event", tags=["events"])
event = Event()


@router.post("/add/{name}")
async def add_event_in_db(name: str, start_event: datetime.datetime = datetime.datetime.now(),
                          end_event: datetime.datetime = datetime.datetime.now(), db: AsyncSession = Depends(get_db)):
    return await event.add(name, start_event, end_event, db)


@router.get("/get/all")
async def get_all_events(db: AsyncSession = Depends(get_db)):
    return await event.get_all(db)


@router.get("/get/")
async def get_events_for_list(id_list: str = Query(..., description="Список идентификаторов, разделенных запятыми"),
                              db: AsyncSession = Depends(get_db)):
    return await event.get_for_id_list(id_list, db)


@router.get("/get/{id}")
async def get_event(id: int, db: AsyncSession = Depends(get_db)):
    return await event.get_for_id(id, db)


@router.delete("/delete/")
async def del_events_from_list_names(id: IdSchemas, db: AsyncSession = Depends(get_db)):
    return await event.del_for_id(id.id, db)
