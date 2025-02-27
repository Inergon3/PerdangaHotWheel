import datetime

from sqlalchemy import MetaData, ForeignKey, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import as_declarative, Mapped, mapped_column, relationship

from config import host, user, password_bd, db_name

metadata = MetaData()
engine = create_async_engine(f"postgresql+asyncpg://{user}:{password_bd}@{host}/{db_name}", echo=True)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


@as_declarative(metadata=metadata)
class AbstractModel:
    pass


class EventModel(AbstractModel):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    start_event: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    end_event: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    members: Mapped[list["MemberModel"]] = relationship(
        "MemberModel",
        secondary="eventmember",
        back_populates="events"
    )

    def __repr__(self):
        return f"Event(id={self.id}, name='{self.name}', start_event='{self.start_event}, end_event='{self.end_event}')"


class MemberModel(AbstractModel):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    events: Mapped[list["EventModel"]] = relationship(
        "EventModel",
        secondary="eventmember",
        back_populates="members"
    )

    games: Mapped[list["GameModel"]] = relationship(
        "GameModel",
        back_populates="member",
        cascade="all, delete-orphan"
    )

    gameWin: Mapped[str] = mapped_column(nullable=True)


class GameModel(AbstractModel):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column()

    user_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))

    member: Mapped["MemberModel"] = relationship(
        "MemberModel",
        back_populates="games"
    )

    def __repr__(self):
        return f"Game(id={self.id}, name='{self.name}', user_id='{self.user_id}, event_id='{self.event_id}')"


class EventMemberModel(AbstractModel):
    __tablename__ = "eventmember"

    event_id = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    member_id = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), primary_key=True)
