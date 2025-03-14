from typing import Optional, Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from crud import Event
from model import get_db
from schemas import IdSchemas, EventSchemas

router = APIRouter(prefix="/events", tags=["events"])
event = Event()


@router.post("/add")
async def add_event_in_db(event1: EventSchemas, db: AsyncSession = Depends(get_db)):
    await event.add(event1.name, event1.event_start, event1.event_end, db)
    return


# @router.get("/get/all")
# async def get_all_events(db: AsyncSession = Depends(get_db)):
#     result = await event.get_all(db)
#     return {
#         "data": result
#     }


@router.get("/get")
async def get_events_for_list(
        id_list: Annotated[Optional[str], Query(description="Список идентификаторов, разделенных запятыми")] = None,
        db: AsyncSession = Depends(get_db)):
    result = await event.get_for_id_list(id_list, db)
    return {
        "data": result
    }


# @router.get("/get/{id}")
# async def get_event(id: int, db: AsyncSession = Depends(get_db)):
#     result = await event.get_for_id(id, db)
#     return {
#         "data": result
#     }


@router.delete("/delete")
async def del_events_from_list_names(id: IdSchemas, db: AsyncSession = Depends(get_db)):
    await event.del_for_id(id.id, db)
    return
