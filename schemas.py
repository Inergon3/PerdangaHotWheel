import datetime
from pydantic import BaseModel


class IdSchemas(BaseModel):
    id: list[int]
class NamesSchemas(BaseModel):
    names: list[str]
class EventSchemas(BaseModel):
    name: str | None = None
    id: int | None = None
    event_start: datetime.datetime = datetime.datetime.now()
    event_end: datetime.datetime = datetime.datetime.now()

class GameSchemas(BaseModel):
    game_name: str | None = None
    event_id: int | None = None
    member_id: int | None = None

class MemberSchemas(BaseModel):
    name: str | None = None
    id: int | None = None

class EventsMembersSchemas(BaseModel):
    event_id: int
    member_id: int
    game_win: str | None = None