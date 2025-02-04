from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import as_declarative, Mapped, mapped_column, relationship

from config import host, user, password_bd, db_name

metadata = MetaData()
engine = create_async_engine(f"postgresql+asyncpg://{user}:{password_bd}@{host}/{db_name}", echo=True)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


@as_declarative()
class AbstractModel:
    pass


class EventModel(AbstractModel):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name_event: Mapped[str] = mapped_column(unique=True)
    members: Mapped["User"] = relationship(back_populates="members.user_name", uselist= False)


class MemberModel(AbstractModel):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    user_name: Mapped[str] = relationship(back_populates="events.members", uselist= True)
    gamesList: Mapped["Games"] = relationship(back_populates="games.name_game", uselist= False)
    #gameWin: Mapped[str] = mapped_column()
    #gamesPool: Mapped[list] = mapped_column()
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))

class GameModel(AbstractModel):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name_game: Mapped[str] = relationship(back_populates="members.gameList", uselist= True)
    user_id: Mapped[int] = mapped_column(ForeignKey("members.id"))