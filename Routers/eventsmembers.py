from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud import Member
from model import get_db

router = APIRouter(prefix="/eventmember", tags=["eventmember"])
member = Member()


@router.post("/add/{name_event}/{name_member}")
async def add_event_for_member(name_event: str, name_member: str, db: AsyncSession = Depends(get_db)):
    return await member.add_in_event(name_member, name_event, db)
