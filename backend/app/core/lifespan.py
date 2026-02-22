from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.mongo import close_mongo_connection, connect_to_mongo, get_database
from app.db.redis import close_redis_connection, connect_to_redis


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_to_mongo()
    await connect_to_redis()

    database = get_database()
    await database["users"].create_index("email", unique=True)

    yield

    await close_redis_connection()
    await close_mongo_connection()
