from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud import  add_event
from model import SessionLocal

app = FastAPI()

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@app.post("/addEvent")
async def addEventInDb(name: str, db: AsyncSession = Depends(get_db)):
    return add_event(name, db)