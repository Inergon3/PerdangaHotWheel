from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from model import MemberModel, EventModel, GameModel


async def add_event(name, db: Session):
    new_event = EventModel(name_event = name)
    db.add(new_event)
    await db.commit()
    return new_event

async def get_all_event(db: Session):
    result = await db.execute(select(EventModel))
    events = result.scalars().all()
    return events

async def add_member(name, db: Session):
    new_member = MemberModel(user_name = name)
    db.add(new_member)
    await db.commit()
    return new_member

async def get_all_member(db: Session):
    result = await db.execute(select(MemberModel))
    members = result.scalars().all()
    return members

async def add_game_player(name_game, name_member, db: Session):
    result = await db.execute(select(MemberModel).filter(MemberModel.user_name == name_member))
    member = result.scalars().first()
    new_game = GameModel(name_game = name_game, user_id = member.id)
    db.add(new_game)
    await db.commit()
    return new_game
