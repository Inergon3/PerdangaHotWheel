from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Crud.objects import member_obj, eventmember_obj
from model import get_db
from schemas import EventsMembersSchemas

router = APIRouter(prefix="/eventmembers", tags=["eventmember"])



@router.post("/add")
async def add_event_for_member(eventmember: EventsMembersSchemas, db: AsyncSession = Depends(get_db)):
    await member_obj.add_in_event(eventmember.member_id, eventmember.event_id, db)
    return


@router.get("get/all")
async def get_all_event_member(db: AsyncSession = Depends(get_db)):
    result = await eventmember_obj.get_all(db)
    return {
        "data": result
    }
