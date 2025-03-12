from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from crud import Member
from model import get_db
from schemas import IdSchemas, MemberSchemas

router = APIRouter(prefix="/members", tags=["members"])
member = Member()


@router.post("/add")
async def add_member_in_db(name: MemberSchemas, db: AsyncSession = Depends(get_db)):
    await member.add(name.name, db)
    return


@router.get("/get/all")
async def get_all_members(db: AsyncSession = Depends(get_db)):
    result = await member.get_all(db)
    return {
        "data": result
    }


@router.get("/get")
async def get_members_for_list(id_list: str = Query(..., description="Список идентификаторов, разделенных запятыми"),
                               db: AsyncSession = Depends(get_db)):
    result = await member.get_for_id_list(id_list, db)
    return {
        "data": result
    }




@router.get("/get/{id}")
async def get_member_for_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await member.get_for_id(id, db)
    return {
        "data": result
    }


@router.delete("/delete")
async def del_members_from_list_id(id_list: IdSchemas, db: AsyncSession = Depends(get_db)):
    await member.del_for_id(id_list.id, db)
    return


@router.get("/get/events/{member_id}")
async def get_events_for_member(member_id: int, db: AsyncSession = Depends(get_db)):
    participates = await member.get_participates_events(member_id, db)
    not_participates = await member.get_not_participates_events(member_id, db)
    return {
        "participates": participates,
        "not_participates": not_participates
    }
