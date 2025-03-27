from datetime import datetime, timedelta

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, APIRouter, Cookie
from fastapi.responses import RedirectResponse
from openid.consumer.consumer import Consumer, SUCCESS
from openid.store.memstore import MemoryStore
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import steam_api_key, SECRET_KEY, JWT_ALGORITHM
from model import get_db, MemberModel

router = APIRouter(prefix="/auth", tags=["auth"])

openid_consumer = Consumer({}, MemoryStore())
openid_consumer.use_stateless = True

STEAM_API_KEY = steam_api_key
JWT_SECRET = SECRET_KEY
JWT_EXPIRE_MINUTES = 60


async def get_steam_user_info(steam_id: str, api_key: str):
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("response", {}).get("players", [])[0]
    return None


def create_jwt_token(steam_id: str):
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": steam_id, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия токена истек")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Неверный токен")


async def get_current_user(token: str = Cookie(None), db: Session = Depends(get_db)):
    """Извлекает токен из cookie и проверяет его."""
    if not token:
        raise HTTPException(status_code=401, detail="Токен отсутствует в cookie")

    steam_id = verify_jwt_token(token)

    stmt = select(MemberModel).where(MemberModel.steam_id == steam_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return user


@router.get("/login")
async def login(request: Request):
    """Перенаправляет пользователя на Steam OpenID."""
    auth_request = openid_consumer.begin("https://steamcommunity.com/openid")
    return_url = request.query_params.get("redirect", "http://localhost:5500/")
    callback_url = str(request.url_for("callback")) + f"?redirect={return_url}"
    redirect_url = auth_request.redirectURL(return_to=callback_url, realm=str(request.base_url))
    return RedirectResponse(redirect_url)


@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    """Обрабатывает ответ от Steam после авторизации."""
    query_params = dict(request.query_params)
    response = openid_consumer.complete(query_params, str(request.url))

    if response.status != SUCCESS:
        raise HTTPException(status_code=401, detail="Ошибка авторизации через Steam")

    steam_id = response.identity_url.split("/")[-1]

    # Получаем имя пользователя из Steam API
    user_info = await get_steam_user_info(steam_id, STEAM_API_KEY)
    user_name = user_info.get("personaname", "Unknown") if user_info else "Unknown"

    # Проверяем, есть ли пользователь в базе
    stmt = select(MemberModel).where(MemberModel.steam_id == steam_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    # Если пользователя нет — создаем его
    if not user:
        user = MemberModel(steam_id=steam_id, name=user_name)
        db.add(user)
        await db.commit()

    # Генерируем JWT токен
    token = create_jwt_token(steam_id)

    return_url = request.query_params.get("redirect", "http://localhost:5500/")

    response = RedirectResponse(url=return_url)
    response.set_cookie(key="token", value=token, httponly=True, max_age=3600, secure=False, samesite="Lax")

    return response


@router.get("/protected")
async def protected_route(user: MemberModel = Depends(get_current_user)):
    """Пример защищенного маршрута, доступного только авторизованным пользователям."""
    return {"message": f"Привет, {user.name}!"}


@router.get("/logout")
async def logout():
    """Выход: удаление JWT cookie."""
    response = RedirectResponse(url="http://localhost:5500/")
    response.delete_cookie("token")
    return response
