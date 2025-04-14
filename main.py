import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from Routers.auth import router as auth_router
from Routers.events import router as events_router
from Routers.eventsmembers import router as eventsmembers_router
from Routers.games import router as games_router
from Routers.members import router as members_router

app = FastAPI()
origins = ["http://localhost:5500",
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
    return {"message": "Welcome!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
