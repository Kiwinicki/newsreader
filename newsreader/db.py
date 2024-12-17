"""A module providing database access."""

import asyncio

import databases
import sqlalchemy
from sqlalchemy.exc import OperationalError, DatabaseError
from sqlalchemy.ext.asyncio import create_async_engine
from asyncpg.exceptions import (  # type: ignore
    CannotConnectNowError,
    ConnectionDoesNotExistError,
)

from newsreader.config import config

metadata = sqlalchemy.MetaData()

user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
)

user_friends_table = sqlalchemy.Table(
    "user_friends",
    metadata,
    sqlalchemy.Column(
        "user_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id"),
        primary_key=True,
    ),
    sqlalchemy.Column(
        "friend_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id"),
        primary_key=True,
    ),
)

user_favorites = sqlalchemy.Table(
    "user_favorites",
    metadata,
    sqlalchemy.Column(
        "user_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id"),
        primary_key=True,
    ),
    sqlalchemy.Column(
        "news_id", sqlalchemy.String, nullable=False, primary_key=True
    ),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
)

db_uri = (
    f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASSWORD}"
    f"@{config.DB_HOST}/{config.DB_NAME}"
)

engine = create_async_engine(
    db_uri,
    echo=True,
    future=True,
    pool_pre_ping=True,
)

database = databases.Database(
    db_uri,
    force_rollback=True,
)


async def init_db(retries: int = 5, delay: int = 5) -> None:
    """Function initializing the DB.

    Args:
        retries (int, optional): Number of retries of connect to DB.
            Defaults to 5.
        delay (int, optional): Delay of connect do DB. Defaults to 2.
    """
    for attempt in range(retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(metadata.create_all)
            return
        except (
            OperationalError,
            DatabaseError,
            CannotConnectNowError,
            ConnectionDoesNotExistError,
        ) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(delay)

    raise ConnectionError("Could not connect to DB after several retries.")
