import jwt
from fastapi import HTTPException, Depends
from fastapi.security import APIKeyCookie

from config import JWT_ALGORITHM, SECRET_KEY

cookie_sec = APIKeyCookie(name="session")
JWT_SECRET = SECRET_KEY


def get_current_user(token: str = Depends(lambda token: token)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        steam_id = payload.get("sub")
        if steam_id is None:
            raise HTTPException(status_code=401, detail="Недействительный токен")
        return steam_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истёк")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Недействительный токен")


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
