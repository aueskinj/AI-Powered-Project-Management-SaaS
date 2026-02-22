import os

import pymongo
import pytest
import redis
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_state() -> None:
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    mongodb_db_name = os.getenv("MONGODB_DB_NAME", "ai_pm_saas")

    mongo_client = pymongo.MongoClient(mongodb_url)
    mongo_client[mongodb_db_name]["users"].delete_many({})
    mongo_client.close()

    redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
    redis_client.flushdb()
    redis_client.close()
