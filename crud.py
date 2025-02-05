from fastapi import HTTPException
from sqlalchemy.orm import Session

from model import MemberModel, EventModel


def add_event(name, db: Session):
    new_event = EventModel(name_event = name)# , members = members)
    db.add(new_event)
    db.commit()
    return new_event