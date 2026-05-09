import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram API ───────────────────────────────────────
API_ID    = int(os.getenv("API_ID", 0))
API_HASH  = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# ── Owner / Sudo ───────────────────────────────────────
OWNER_ID = int(os.getenv("OWNER_ID", 423346191))

# ── Assistant (user account for VC streaming) ──────────
# Run generate_session.py once, then:
# heroku config:set STRING_SESSION="xxxx"
STRING_SESSION = os.getenv("STRING_SESSION", "")

# ── MongoDB ────────────────────────────────────────────
# heroku config:set MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/shinubot"
MONGO_URI = os.getenv("MONGO_URI", "")

# ── YouTube Data API v3 ────────────────────────────────
# heroku config:set YOUTUBE_API_KEY="AIzaSy..."
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# ── YouTube Cookies (full cookies.txt content) ─────────
# Export from browser using "Get cookies.txt" extension on youtube.com
# heroku config:set YOUTUBE_COOKIES="$(cat cookies.txt)"
YOUTUBE_COOKIES = os.getenv("YOUTUBE_COOKIES", "")

# ── Bot identity ───────────────────────────────────────
BOT_NAME    = "Shinu Music Bot"
BOT_VERSION = "2.0.0"

# ── Lyrics API (Genius) ────────────────────────────────
# heroku config:set GENIUS_TOKEN="your_token"
GENIUS_TOKEN = os.getenv("GENIUS_TOKEN", "")

# ── Queue / misc ───────────────────────────────────────
MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", 50))

# ── Validation ─────────────────────────────────────────
if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError(
        "Missing required env vars: API_ID, API_HASH, BOT_TOKEN\n"
        "Add them in Heroku Dashboard → Settings → Config Vars"
    )
