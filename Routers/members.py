from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from crud import Member
from model import get_db
from schemas import NamesSchemas

router = APIRouter(prefix="/member", tags=["members"])
member = Member()


@router.post("/add/{name}")
async def add_member_in_db(name: str, db: AsyncSession = Depends(get_db)):
    return await member.add(name, db)


@router.get("/get/all")
async def get_all_members(db: AsyncSession = Depends(get_db)):
    return await member.get_all(db)


@router.get("/get/")
async def get_members_for_list(id_list: str = Query(..., description="Список идентификаторов, разделенных запятыми"),
                               db: AsyncSession = Depends(get_db)):
    return await member.get_for_id_list(id_list, db)


@router.get("/get/{id}")
async def get_member_for_id(id: int, db: AsyncSession = Depends(get_db)):
    return await member.get_for_id(id, db)


@router.delete("/delete/")
async def del_members_from_list_names(name: NamesSchemas, db: AsyncSession = Depends(get_db)):
    return await member.del_for_name(name.names, db)


@router.get("/get/events/{member_id}")
async def get_events_for_member(member_id: int, db: AsyncSession = Depends(get_db)):
    participates = await member.get_participates_events(member_id, db)
    not_participates = await member.get_not_participates_events(member_id, db)
    return {
        "Учавствует": participates,
        "Не учавствует": not_participates
    }
