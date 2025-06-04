"""
MongoDB connection setup for WarehouseVision AI using Motor.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from src.config.settings import get_settings

settings = get_settings()

# Create MongoDB async client
mongo_client = AsyncIOMotorClient(settings.DATABASE_URL)

db = mongo_client.get_default_database()
