from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Crud.objects import member_obj, eventmember_obj
from Routers.auth import get_current_user
from model import get_db, MemberModel
from schemas import EventsMembersSchema

router = APIRouter(prefix="/eventmembers", tags=["eventmember"])


@router.post("/add")
async def add_event_for_member(eventmember: EventsMembersSchema, db: AsyncSession = Depends(get_db),
                               user: MemberModel = Depends(get_current_user)):
    await member_obj.add_in_event(eventmember.member_id, eventmember.event_id, db)
    return


@router.get("get/all")
async def get_all_event_member(db: AsyncSession = Depends(get_db), user: MemberModel = Depends(get_current_user)):
    result = await eventmember_obj.get_all(db)
    return {
        "data": result
    }
