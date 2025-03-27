import jwt
from fastapi import HTTPException, Depends, Cookie
from fastapi.security import APIKeyCookie
from requests import Session
from sqlalchemy import select

from Routers.auth import verify_jwt_token
from config import JWT_ALGORITHM, SECRET_KEY
from model import get_db, MemberModel

cookie_sec = APIKeyCookie(name="session")
JWT_SECRET = SECRET_KEY



async def valid_count_id(id_list1, id_list2):
    if len(id_list1) != len(id_list2):
        found_ids = {event.id for event in id_list1}
        missing_ids = [id for id in id_list2 if id not in found_ids]
        raise HTTPException(status_code=404, detail={
            "message": "Object with the following IDs were not found:",
            "not found object": missing_ids
        })


async def str_list_to_int_list(id_list):
    if isinstance(id_list, str):
        id_list_str = id_list.split(",")
        id_list = []
        for id in id_list_str:
            id_list.append(int(id))
    return id_list


async def auth(user):
    if not user:
        raise HTTPException(status_code=403, detail="Not auth")
