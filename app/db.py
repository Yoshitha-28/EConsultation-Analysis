from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from .config import settings

client_async = AsyncIOMotorClient(settings.mongodb_uri)
db_async = client_async[settings.mongo_db]

client_sync = MongoClient(settings.mongodb_uri)
db_sync = client_sync[settings.mongo_db]