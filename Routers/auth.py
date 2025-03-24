import os

import httpx
from fastapi import Depends, HTTPException, Request, Response, APIRouter
from fastapi.responses import RedirectResponse
from openid.consumer.consumer import Consumer, SUCCESS
from openid.store.filestore import FileOpenIDStore
from sqlalchemy import select
from sqlalchemy.orm import Session

from Crud.crud import get_current_user
from config import steam_api_key
from model import get_db, MemberModel

router = APIRouter(prefix="/auth", tags=["auth"])

STORE_PATH = "./openid_store"
if not os.path.exists(STORE_PATH):
    os.makedirs(STORE_PATH)
store = FileOpenIDStore(STORE_PATH)
openid_consumer = Consumer({}, store)

STEAM_API_KEY = steam_api_key


async def get_steam_user_info(steam_id: str, api_key: str):
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("response", {}).get("players", [])[0]
        else:
            raise HTTPException(status_code=400, detail="Не удалось получить информацию о пользователе")


@router.get("/login")
async def login(request: Request):
    """ Перенаправление пользователя на страницу авторизации Steam """
    auth_request = openid_consumer.begin("https://steamcommunity.com/openid")

    # Получаем URL возврата (если был передан)
    return_url = request.query_params.get("redirect", "http://localhost:5500/")

    # Сохраняем return_url в параметрах колбэка
    callback_url = str(request.url_for("callback")) + f"?redirect={return_url}"

    redirect_url = auth_request.redirectURL(
        return_to=callback_url,
        realm=str(request.base_url)
    )
    return RedirectResponse(redirect_url)


@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    """ Обработка ответа от Steam после авторизации """
    query_params = dict(request.query_params)
    response = openid_consumer.complete(query_params, str(request.url))

    if response.status == SUCCESS:
        steam_id_int = response.identity_url.split('/')[-1]
        steam_id_str = str(steam_id_int)

        user_info = await get_steam_user_info(steam_id_int, STEAM_API_KEY)
        user_name = user_info.get("personaname", "Unknown") if user_info else "Unknown"

        # Проверяем, есть ли пользователь в базе
        stmt = select(MemberModel).where(MemberModel.steam_id == steam_id_str)
        result = await db.execute(stmt)
        user = result.scalars().first()

        # Если пользователя нет, создаем его
        if not user:
            user = MemberModel(steam_id=steam_id_str, name=user_name)
            db.add(user)
            await db.commit()

        # Получаем redirect URL, переданный при авторизации
        return_url = request.query_params.get("redirect", "http://localhost:5500/")

        # Создаем ответ и устанавливаем cookie
        response = RedirectResponse(url=return_url)
        response.set_cookie(key="session", value=steam_id_str, httponly=True, max_age=3600)

        return response
    else:
        raise HTTPException(status_code=401, detail="Ошибка авторизации")


@router.get("/protected")
async def protected_route(user: MemberModel = Depends(get_current_user)):
    return {"message": f"Привет, {user.name}!"}
