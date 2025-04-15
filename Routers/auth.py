from datetime import datetime, timedelta

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, APIRouter, Cookie
from fastapi.responses import RedirectResponse
from openid.consumer.consumer import Consumer, SUCCESS
from openid.store.memstore import MemoryStore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import APP_CONFIG
from model import get_db, MemberModel

router = APIRouter(prefix="/auth", tags=["auth"])

openid_consumer = Consumer({}, MemoryStore())
openid_consumer.use_stateless = True

STEAM_API_KEY = APP_CONFIG["steam_api_key"]
JWT_SECRET = APP_CONFIG["secret_key"]
JWT_EXPIRE_MINUTES = 60

const_return_url = "http://localhost:8000/docs"


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
    return jwt.encode(payload, JWT_SECRET, algorithm=APP_CONFIG["jwt_algorithm"])


def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[APP_CONFIG["jwt_algorithm"]])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия токена истек")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Неверный токен")


async def get_current_user(token: str = Cookie(None), db: AsyncSession = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Токен не предоставлен")
    steam_id = verify_jwt_token(token)
    query = select(MemberModel).where(MemberModel.steam_id == steam_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user


@router.get("/login")
async def login(request: Request):
    auth_request = openid_consumer.begin("https://steamcommunity.com/openid")
    return_url = request.query_params.get("redirect", const_return_url)
    callback_url = str(request.url_for("callback")) + f"?redirect={return_url}"
    redirect_url = auth_request.redirectURL(return_to=callback_url, realm=str(request.base_url))
    return RedirectResponse(redirect_url)


@router.get("/callback")
async def callback(request: Request, db: AsyncSession = Depends(get_db)):
    query_params = dict(request.query_params)
    response = openid_consumer.complete(query_params, str(request.url))

    if response.status != SUCCESS:
        raise HTTPException(status_code=401, detail="Ошибка авторизации через Steam")

    steam_id = response.identity_url.split("/")[-1]

    user_info = await get_steam_user_info(steam_id, STEAM_API_KEY)
    user_name = user_info.get("personaname", "Unknown") if user_info else "Unknown"

    stmt = select(MemberModel).where(MemberModel.steam_id == steam_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        user = MemberModel(steam_id=steam_id, name=user_name)
        db.add(user)
        await db.commit()

    token = create_jwt_token(steam_id)

    return_url = request.query_params.get("redirect", const_return_url)

    response = RedirectResponse(url=return_url)
    response.set_cookie(key="token", value=token, httponly=True, max_age=3600, secure=False, samesite="Lax")
    response.set_cookie(key="user", value=user_info, httponly=False, max_age=3600, secure=False, samesite="Lax")

    return response


@router.get("/protected")
async def protected_route(user: MemberModel = Depends(get_current_user)):
    return {"message": f"Привет, {user.name}!"}


@router.get("/logout")
async def logout():
    response = RedirectResponse(url=const_return_url)
    response.delete_cookie("token")
    return response
