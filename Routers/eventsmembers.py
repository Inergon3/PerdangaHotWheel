from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud import Member, EventMember
from model import get_db

router = APIRouter(prefix="/eventmember", tags=["eventmember"])
member = Member()
event_members = EventMember()


@router.post("/add/id_event={id_event},id_member={id_member}")
async def add_event_for_member(id_event: int, id_member: int, db: AsyncSession = Depends(get_db)):
    return await member.add_in_event(id_member, id_event, db)

@router.get("get/all")
async def get_all_event_member(db: AsyncSession = Depends(get_db)):
    return await event_members.get_all(db)
