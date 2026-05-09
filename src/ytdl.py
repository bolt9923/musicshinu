import asyncio
import os
import re
import tempfile
import logging
from typing import Optional
import yt_dlp
from googleapiclient.discovery import build

from src.queue import Track
from config.settings import YOUTUBE_API_KEY, YOUTUBE_COOKIES

logger = logging.getLogger(__name__)

# ── Cookies file (written from env var at runtime) ────────────────────────────
_COOKIES_FILE: Optional[str] = None

def _get_cookies_file() -> Optional[str]:
    """
    Write YOUTUBE_COOKIES env var content to a temp file and return its path.
    yt-dlp needs a file path, not a string.
    """
    global _COOKIES_FILE
    if _COOKIES_FILE and os.path.exists(_COOKIES_FILE):
        return _COOKIES_FILE

    if not YOUTUBE_COOKIES:
        return None

    try:
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, prefix="yt_cookies_"
        )
        tmp.write(YOUTUBE_COOKIES)
        tmp.close()
        _COOKIES_FILE = tmp.name
        logger.info(f"YouTube cookies written to {_COOKIES_FILE}")
        return _COOKIES_FILE
    except Exception as e:
        logger.warning(f"Could not write cookies file: {e}")
        return None


def _build_ydl_opts(playlist: bool = False) -> dict:
    """Build yt-dlp options, injecting cookies if available."""
    opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": not playlist,
        "default_search": "ytsearch",
    }
    if playlist:
        opts["extract_flat"] = True

    cookies_file = _get_cookies_file()
    if cookies_file:
        opts["cookiefile"] = cookies_file

    return opts


# ── YouTube Data API v3 search ────────────────────────────────────────────────

def _search_via_api(query: str) -> Optional[str]:
    """
    Use YouTube Data API v3 to find the best video URL for a query.
    Falls back to yt-dlp search if API key is not set or quota exceeded.
    """
    if not YOUTUBE_API_KEY:
        return None
    try:
        youtube = build("googleapiclient", "v3", developerKey=YOUTUBE_API_KEY,
                        cache_discovery=False)
        request = youtube.search().list(
            part="id",
            q=query,
            type="video",
            maxResults=1,
            videoCategoryId="10",  # Music category
        )
        response = request.execute()
        items = response.get("items", [])
        if items:
            video_id = items[0]["id"]["videoId"]
            url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"YouTube API found: {url}")
            return url
    except Exception as e:
        logger.warning(f"YouTube API search failed (falling back to yt-dlp): {e}")
    return None


# ── Single track ──────────────────────────────────────────────────────────────

async def search_youtube(query: str) -> Optional[Track]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _extract_single, query)


def _extract_single(query: str) -> Optional[Track]:
    is_url = bool(re.match(r"https?://", query))

    # If not a URL, try YouTube API first for better results
    if not is_url:
        api_url = _search_via_api(query)
        if api_url:
            query = api_url
            is_url = True

    search_query = query if is_url else f"ytsearch:{query}"
    opts = _build_ydl_opts()

    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(search_query, download=False)
            if not info:
                return None
            if "entries" in info:
                info = info["entries"][0]
            if not info:
                return None
            if not info.get("url"):
                info = ydl.extract_info(info["webpage_url"], download=False)

            audio_url = _pick_audio_url(info)
            if not audio_url:
                return None

            return Track(
                title=info.get("title", "Unknown"),
                url=audio_url,
                webpage_url=info.get("webpage_url", query),
                duration=int(info.get("duration") or 0),
                requester="",
            )
        except yt_dlp.utils.DownloadError as e:
            logger.warning(f"yt-dlp error: {e}")
            return None


# ── Playlist ──────────────────────────────────────────────────────────────────

async def extract_playlist(url: str) -> list[Track]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _extract_playlist, url)


def _extract_playlist(url: str) -> list[Track]:
    opts = _build_ydl_opts(playlist=True)
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if not info or "entries" not in info:
                return []
            tracks = []
            for entry in info["entries"][:50]:
                if not entry:
                    continue
                tracks.append(Track(
                    title=entry.get("title", "Unknown"),
                    url="",
                    webpage_url=entry.get("url") or entry.get("webpage_url", ""),
                    duration=int(entry.get("duration") or 0),
                    requester="",
                ))
            return tracks
        except yt_dlp.utils.DownloadError:
            return []


async def resolve_track_url(track: Track) -> Optional[Track]:
    """Fetch real stream URL for a playlist track (called just before playing)."""
    if track.url:
        return track
    resolved = await search_youtube(track.webpage_url)
    if resolved:
        track.url = resolved.url
        track.duration = resolved.duration
    return track if track.url else None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _pick_audio_url(info: dict) -> Optional[str]:
    formats = info.get("formats", [])
    audio_only = [f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none"]
    if audio_only:
        for fmt in reversed(audio_only):
            if fmt.get("ext") in ("opus", "webm", "m4a"):
                return fmt["url"]
        return audio_only[-1]["url"]
    return info.get("url")


def format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "Live"
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def is_playlist_url(url: str) -> bool:
    return bool(re.search(r"[?&]list=", url))
