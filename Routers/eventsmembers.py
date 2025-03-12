from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing import db

from crud import Member, EventMember
from model import get_db
from schemas import EventsMembersSchemas

router = APIRouter(prefix="/eventmembers", tags=["eventmember"])
member = Member()
event_members = EventMember()


@router.post("/add")
async def add_event_for_member(eventmember: EventsMembersSchemas, db: AsyncSession = Depends(get_db)):
    await member.add_in_event(eventmember.id_member, eventmember.id_event, db)
    return

@router.get("get/all")
async def get_all_event_member(db: AsyncSession = Depends(get_db)):
    result = await event_members.get_all(db)
    return {
        "data": result
    }
