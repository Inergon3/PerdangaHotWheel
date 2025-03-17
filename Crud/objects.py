from Crud.Event import Event
from Crud.EventMember import EventMember
from Crud.Game import Game
from Crud.Member import Member

event_obj = Event()
member_obj = Member(event_obj)
game_obj = Game(event_obj, member_obj)
eventmember_obj = EventMember(event_obj, member_obj, game_obj)
