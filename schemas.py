import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class IdSchema(BaseModel):
    id: List[int] = Field(..., description="List of IDs")


class NamesSchema(BaseModel):
    names: List[str] = Field(..., description="List of names")


class EventSchema(BaseModel):
    name: Optional[str] = Field(None, description="Event name")
    id: Optional[int] = Field(None, description="Event ID")
    event_start: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Event start time")
    event_end: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Event end time")


class GameSchema(BaseModel):
    game_name: Optional[str] = Field(None, description="Game name")
    event_id: Optional[int] = Field(None, description="Event ID")
    member_id: Optional[int] = Field(None, description="Member ID")


class MemberSchema(BaseModel):
    name: Optional[str] = Field(None, description="Member name")
    id: Optional[int] = Field(None, description="Member ID")


class EventsMembersSchema(BaseModel):
    event_id: int = Field(..., description="Event ID")
    member_id: int = Field(..., description="Member ID")
    game_win: Optional[str] = Field(None, description="Winning game")