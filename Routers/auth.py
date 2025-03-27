from datetime import datetime, timedelta

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, APIRouter
from fastapi.responses import RedirectResponse
from openid.consumer.consumer import Consumer, SUCCESS
from openid.store.memstore import MemoryStore  # Используем MemoryStore вместо FileOpenIDStore
from sqlalchemy import select
from sqlalchemy.orm import Session

from Crud.crud import get_current_user
from config import steam_api_key, SECRET_KEY, JWT_ALGORITHM
from model import get_db, MemberModel

router = APIRouter(prefix="/auth", tags=["auth"])

# Используем MemoryStore вместо FileOpenIDStore
openid_consumer = Consumer({}, MemoryStore())
openid_consumer.use_stateless = True  # Включаем stateless mode

STEAM_API_KEY = steam_api_key
JWT_SECRET = SECRET_KEY
JWT_EXPIRE_MINUTES = 60  # Время жизни JWT токена (в минутах)


async def get_steam_user_info(steam_id: str, api_key: str):
    """Запрашивает информацию о пользователе через Steam Web API."""
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("response", {}).get("players", [])[0]
    return None


def create_jwt_token(steam_id: str):
    """Создает JWT токен для авторизации пользователя."""
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": steam_id, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.get("/login")
async def login(request: Request):
    """Перенаправляет пользователя на Steam OpenID для входа."""
    auth_request = openid_consumer.begin("https://steamcommunity.com/openid")

    return_url = request.query_params.get("redirect", "http://localhost:5500/")
    callback_url = str(request.url_for("callback")) + f"?redirect={return_url}"

    redirect_url = auth_request.redirectURL(return_to=callback_url, realm=str(request.base_url))
    return RedirectResponse(redirect_url)


@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    """Обрабатывает ответ от Steam после авторизации."""
    query_params = dict(request.query_params)

    # Используем stateless mode для аутентификации
    response = openid_consumer.complete(query_params, str(request.url))

    if response.status != SUCCESS:
        raise HTTPException(status_code=401, detail="Ошибка авторизации через Steam")

    steam_id_int = response.identity_url.split("/")[-1]
    steam_id_str = str(steam_id_int)

    # Получаем имя пользователя из Steam API
    user_info = await get_steam_user_info(steam_id_int, STEAM_API_KEY)
    user_name = user_info.get("personaname", "Unknown") if user_info else "Unknown"

    # Проверяем, есть ли пользователь в базе
    stmt = select(MemberModel).where(MemberModel.steam_id == steam_id_str)
    result = await db.execute(stmt)
    user = result.scalars().first()

    # Если пользователя нет — создаем его
    if not user:
        user = MemberModel(steam_id=steam_id_str, name=user_name)
        db.add(user)
        await db.commit()

    # Генерируем JWT токен
    token = create_jwt_token(steam_id_str)

    return_url = request.query_params.get("redirect", "http://localhost:5500/")

    # Устанавливаем JWT в cookie
    response = RedirectResponse(url=return_url)
    response.set_cookie(key="token", value=token, httponly=True, max_age=3600)

    return response


@router.get("/protected")
async def protected_route(user: MemberModel = Depends(get_current_user)):
    """Пример защищенного маршрута, доступного только авторизованным пользователям."""
    return {"message": f"Привет, {user.name}!"}
