from sqlalchemy import MetaData, ForeignKey, Column, Table
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import as_declarative, Mapped, mapped_column, relationship

from config import host, user, password_bd, db_name

metadata = MetaData()
engine = create_async_engine(f"postgresql+asyncpg://{user}:{password_bd}@{host}/{db_name}", echo=True)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

event_member_association = Table(
    "event_member_association",
    metadata,
    Column("event_id", ForeignKey("events.id"), primary_key=True),
    Column("member_id", ForeignKey("members.id"), primary_key=True)
)


@as_declarative(metadata=metadata)
class AbstractModel:
    pass


class EventModel(AbstractModel):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name_event: Mapped[str] = mapped_column()
    members: Mapped[list["MemberModel"]] = relationship(
        "MemberModel",
        secondary=event_member_association,
        back_populates="events"
    )


class MemberModel(AbstractModel):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    user_name: Mapped[str] = mapped_column(unique=True)
    events: Mapped[list["EventModel"]] = relationship(
        "EventModel",
        secondary=event_member_association,
        back_populates="members"
    )
    gameWin: Mapped[str] = mapped_column()


class GameModel(AbstractModel):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name_game: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
