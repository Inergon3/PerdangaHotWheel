from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from Crud.objects import member_obj, eventmember_obj
from Routers.auth import get_current_user
from model import get_db, MemberModel
from schemas import IdSchema, MemberSchema, EventsMembersSchema

router = APIRouter(prefix="/members", tags=["members"])


@router.post("/add")
async def add_member_in_db(name: MemberSchema, db: AsyncSession = Depends(get_db),
                           user: MemberModel = Depends(get_current_user)):
    await member_obj.add(name.name, db)
    return


# @router.get("/get/all")
# async def get_all_members(db: AsyncSession = Depends(get_db)):
#     result = await member.get_all(db)
#     return {
#         "data": result
#     }


@router.get("/get")
async def get_members_for_list(
        id_list: Optional[str] = Query(default=None, description="Список идентификаторов, разделенных запятыми"),
        db: AsyncSession = Depends(get_db), user: MemberModel = Depends(get_current_user)):
    result = await member_obj.get_for_id_list(id_list, db)
    return {
        "data": result
    }


# @router.get("/get/{id}")
# async def get_member_for_id(id: int, db: AsyncSession = Depends(get_db)):
#     result = await member.get_for_id(id, db)
#     return {
#         "data": result
#     }


@router.delete("/delete")
async def del_members_from_list_id(id_list: IdSchema, db: AsyncSession = Depends(get_db),
                                   user: MemberModel = Depends(get_current_user)):
    await member_obj.del_for_id(id_list.id, db)
    return


@router.get("/get/events/{member_id}")
async def get_events_for_member(member_id: int, db: AsyncSession = Depends(get_db),
                                user: MemberModel = Depends(get_current_user)):
    participates = await member_obj.get_participates_events(member_id, db)
    not_participates = await member_obj.get_not_participates_events(member_id, db)
    return {
        "participates": participates,
        "not_participates": not_participates
    }


@router.post("/add/win_game")
async def add_win_game(parametrs: EventsMembersSchema, db: AsyncSession = Depends(get_db),
                       user: MemberModel = Depends(get_current_user)):
    result = await eventmember_obj.add_win_game(parametrs.member_id, parametrs.event_id, db)
    return {
        "data": result
    }
