import datetime
from pydantic import BaseModel


class EventSchemas(BaseModel):
    id: int
    name: str
    start_event: datetime.datetime
    end_event: datetime.datetime

class MemberSchemas(BaseModel):
    id: int
    name: str
    game_win: str

class GameSchemas(BaseModel):
    id: int
    name: str
    user_id: int
    event_id: int

class EventMemberSchemas(BaseModel):
    event_id: int
    member_id: int

class IdSchemas(BaseModel):
    id: list[int]
class NamesSchemas(BaseModel):
    names: list[str]