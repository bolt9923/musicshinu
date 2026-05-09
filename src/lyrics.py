import asyncio
import re
import logging
from typing import Optional
import aiohttp

logger = logging.getLogger(__name__)

GENIUS_SEARCH_URL = "https://api.genius.com/search"
GENIUS_SONG_URL   = "https://api.genius.com/songs/{id}"


async def fetch_lyrics(query: str, token: str) -> Optional[dict]:
    """
    Search Genius for a song and return:
      {"title": ..., "artist": ..., "lyrics": ..., "url": ...}
    or None if not found.
    """
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        # Step 1: search
        async with session.get(
            GENIUS_SEARCH_URL,
            params={"q": query},
            headers=headers,
        ) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()

        hits = data.get("response", {}).get("hits", [])
        if not hits:
            return None

        hit = hits[0]["result"]
        title  = hit.get("title", "Unknown")
        artist = hit.get("primary_artist", {}).get("name", "Unknown")
        song_url = hit.get("url", "")

        # Step 2: scrape lyrics page (Genius API doesn't serve lyrics directly)
        lyrics = await _scrape_lyrics(session, song_url)

        return {
            "title": title,
            "artist": artist,
            "lyrics": lyrics or "Lyrics not available.",
            "url": song_url,
        }


async def _scrape_lyrics(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    """Very light scrape of the Genius lyrics page."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                return None
            html = await resp.text()

        # Remove script/style tags
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        html = re.sub(r"<style[^>]*>.*?</style>",  "", html, flags=re.DOTALL)

        # Find lyrics containers
        containers = re.findall(
            r'data-lyrics-container="true"[^>]*>(.*?)</div>',
            html, flags=re.DOTALL
        )
        if not containers:
            return None

        raw = "\n".join(containers)
        # Replace <br> with newlines, strip remaining tags
        raw = re.sub(r"<br\s*/?>", "\n", raw)
        raw = re.sub(r"<[^>]+>", "", raw)
        # Clean up HTML entities
        raw = raw.replace("&amp;", "&").replace("&quot;", '"') \
                 .replace("&#x27;", "'").replace("&apos;", "'")
        return raw.strip()
    except Exception as e:
        logger.warning(f"Lyrics scrape failed: {e}")
        return None


def chunk_lyrics(lyrics: str, max_len: int = 4000) -> list[str]:
    """Split long lyrics into Telegram-safe chunks."""
    lines = lyrics.split("\n")
    chunks, current = [], []
    length = 0
    for line in lines:
        if length + len(line) + 1 > max_len:
            chunks.append("\n".join(current))
            current, length = [], 0
        current.append(line)
        length += len(line) + 1
    if current:
        chunks.append("\n".join(current))
    return chunks
