import asyncio
import logging
from pyrogram import Client
from pytgcalls import PyTgCalls
from config.settings import (
    API_ID, API_HASH, BOT_TOKEN,
    STRING_SESSION, BOT_NAME, BOT_VERSION,
    MONGO_URI, YOUTUBE_API_KEY, YOUTUBE_COOKIES,
)
from src.handlers import register_handlers
from src.database import connect as db_connect, disconnect as db_disconnect

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    # ── MongoDB ────────────────────────────────────────────────────────
    await db_connect()

    # ── Log which optional features are active ─────────────────────────
    logger.info(f"MongoDB:          {'✅ connected' if MONGO_URI else '⚠️  not set (MONGO_URI missing)'}")
    logger.info(f"YouTube API:      {'✅ enabled'   if YOUTUBE_API_KEY else '⚠️  not set (yt-dlp search fallback)'}")
    logger.info(f"YouTube Cookies:  {'✅ loaded'    if YOUTUBE_COOKIES else '⚠️  not set (age-restricted videos may fail)'}")

    # ── Bot client (handles commands) ─────────────────────────────────
    bot = Client(
        "shinu_music_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
    )

    # ── Assistant client (joins VC and streams audio) ──────────────────
    if not STRING_SESSION:
        raise ValueError(
            "STRING_SESSION is not set!\n"
            "Run: python generate_session.py\n"
            "Then: heroku config:set STRING_SESSION=xxxx"
        )

    assistant = Client(
        "shinu_assistant",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION,
    )

    # ── PyTgCalls uses ASSISTANT to stream in VC ───────────────────────
    call_py = PyTgCalls(assistant)

    register_handlers(bot, call_py)

    logger.info(f"Starting {BOT_NAME} v{BOT_VERSION}…")
    await bot.start()
    await assistant.start()
    await call_py.start()

    bot_me  = await bot.get_me()
    asst_me = await assistant.get_me()
    logger.info(f"Bot:       @{bot_me.username}")
    logger.info(f"Assistant: @{asst_me.username} (streams in VC)")
    logger.info(f"{BOT_NAME} is live! 🎵")

    try:
        await asyncio.get_event_loop().create_future()  # run forever
    finally:
        await db_disconnect()


if __name__ == "__main__":
    asyncio.run(main())
