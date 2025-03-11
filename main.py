import uvicorn
from fastapi import FastAPI

from Routers.events import router as events_router
from Routers.eventsmembers import router as eventsmembers_router
from Routers.games import router as games_router
from Routers.members import router as members_router

app = FastAPI()

app.include_router(events_router)
app.include_router(members_router)
app.include_router(games_router)
app.include_router(eventsmembers_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the main page!"}



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
