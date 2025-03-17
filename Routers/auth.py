from authlib.integrations.starlette_client import OAuth
from fastapi import Request, APIRouter
from starlette.config import Config

from config import steam_api_key

router = APIRouter(prefix="/auth", tags=["auth"])
config_data = {
    'STEAM_OPENID_URL': 'https://steamcommunity.com/openid',
    'STEAM_API_KEY': steam_api_key
}
config = Config(environ=config_data)

oauth = OAuth(config)
oauth.register(
    name='steam',
    client_id=None,
    client_secret=None,
    authorize_url='https://steamcommunity.com/openid/login',
    access_token_url=None,
    api_base_url='https://api.steampowered.com/',
    client_kwargs={'scope': 'openid'},
)


@router.get("/auth/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.steam.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.steam.authorize_access_token(request)
    userinfo = await oauth.steam.parse_id_token(request, token)
    return {"userinfo": userinfo}
