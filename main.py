import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from Routers.auth import router as auth_router
from Routers.events import router as events_router
from Routers.eventsmembers import router as eventsmembers_router
from Routers.games import router as games_router
from Routers.members import router as members_router

app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "https://localhost:8000",
    "http://127.0.0.1:8000",
    "https://steamcommunity.com",
    "http://localhost:8000/docs",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(events_router)
app.include_router(members_router)
app.include_router(games_router)
app.include_router(eventsmembers_router)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the main page!"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
