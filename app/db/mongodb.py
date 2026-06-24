from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging

# Monkeypatch AsyncIOMotorClient to support append_metadata for Beanie/PyMongo 4+ compatibility
if not hasattr(AsyncIOMotorClient, "append_metadata"):
    def append_metadata(self, *args, **kwargs):
        return self.delegate.append_metadata(*args, **kwargs)
    AsyncIOMotorClient.append_metadata = append_metadata

from app.core.config import settings
from app.models.resume import Resume

logger = logging.getLogger(__name__)

async def init_db():
    """
    Initialize MongoDB connection and Beanie ODM.
    """
    try:
        # Create Motor client
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        
        # Initialize beanie with the Resume document class
        await init_beanie(
            database=client[settings.MONGODB_DB_NAME],
            document_models=[Resume]
        )
        logger.info("Successfully connected to MongoDB and initialized Beanie.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise e
