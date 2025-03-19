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

# Настройка хранилища OpenID
STORE_PATH = "./openid_store"
if not os.path.exists(STORE_PATH):
    os.makedirs(STORE_PATH)
store = FileOpenIDStore(STORE_PATH)
openid_consumer = Consumer({}, store)

# Настройка куки


# Steam API Key
STEAM_API_KEY = steam_api_key  # Замените на ваш Steam API Key


# Получение текущего пользователя



# Получение информации о пользователе через Steam API
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
    auth_request = openid_consumer.begin("https://steamcommunity.com/openid")
    redirect_url = auth_request.redirectURL(
        return_to=str(request.url_for("callback")),
        realm=str(request.base_url)
    )
    return RedirectResponse(redirect_url)


@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    query_params = dict(request.query_params)
    response = openid_consumer.complete(query_params, str(request.url))
    if response.status == SUCCESS:
        steam_id_int = response.identity_url.split('/')[-1]
        steam_id_str = str(steam_id_int)
        # Получаем информацию о пользователе через Steam API
        user_info = await get_steam_user_info(steam_id_int, STEAM_API_KEY)

        # Если информация о пользователе получена, используем его имя
        if user_info:
            user_name = user_info.get("personaname", "Unknown")
        else:
            user_name = "Unknown"

        # Проверяем, есть ли пользователь в базе данных
        stmt = select(MemberModel).where(MemberModel.steam_id == steam_id_str)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if not user:
            # Создаем нового пользователя с именем из Steam
            user = MemberModel(steam_id=steam_id_str, name=user_name)
            db.add(user)
            await db.commit()

        # Устанавливаем куки с Steam ID
        session_response = Response("Авторизация успешна")
        session_response.set_cookie(key="session", value=steam_id_int)
        return session_response
    else:
        raise HTTPException(status_code=401, detail="Ошибка авторизации")


@router.get("/protected")
async def protected_route(user: MemberModel = Depends(get_current_user)):
    return {"message": f"Привет, {user.name}!"}