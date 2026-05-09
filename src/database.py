"""
MongoDB connection manager.
All sensitive credentials come from Heroku config vars — never hardcoded.
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import MONGO_URI

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_db = None


async def connect():
    """Connect to MongoDB. Called once at bot startup."""
    global _client, _db
    if not MONGO_URI:
        logger.warning(
            "MONGO_URI not set — MongoDB features disabled. "
            "Add it in Heroku: heroku config:set MONGO_URI=mongodb+srv://..."
        )
        return

    try:
        _client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Verify connection
        await _client.admin.command("ping")
        _db = _client.get_default_database()
        logger.info(f"MongoDB connected: {_db.name}")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        _client = None
        _db = None


async def disconnect():
    global _client
    if _client:
        _client.close()
        _client = None
        logger.info("MongoDB disconnected.")


def get_db():
    """Return the database instance (or None if not connected)."""
    return _db


def is_connected() -> bool:
    return _db is not None
