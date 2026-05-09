import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import StreamAudioEnded

from config.settings import GENIUS_TOKEN
from src.strings import S
from src.queue import get_queue
from src.ytdl import (
    search_youtube, extract_playlist, format_duration, is_playlist_url
)
from src.player import (
    join_and_play, play_next, stop_player,
    pause_player, resume_player, change_volume
)
from src.admin import is_admin
from src.lyrics import fetch_lyrics, chunk_lyrics

logger = logging.getLogger(__name__)


def _name(msg: Message) -> str:
    u = msg.from_user
    return f"@{u.username}" if u.username else u.first_name


async def _reply(msg: Message, text: str):
    await msg.reply_text(text, quote=True, disable_web_page_preview=True)


def register_handlers(app: Client, call_py: PyTgCalls):

    # ── /play ──────────────────────────────────────────────────────────
    @app.on_message(filters.command(["play", "p"]) & filters.group)
    async def play_cmd(client: Client, msg: Message):
        if len(msg.command) < 2:
            await _reply(msg, "❌ Usage: `/play <song name or YouTube URL>`")
            return

        query = " ".join(msg.command[1:])

        # ── Playlist ──────────────────────────────────────────────────
        if is_playlist_url(query):
            status = await _reply(msg, S.PLAYLIST_LOADING)
            tracks = await extract_playlist(query)
            if not tracks:
                await status.edit_text(S.PLAYLIST_EMPTY)
                return

            queue = get_queue(msg.chat.id)
            added = 0
            first_track = None

            for t in tracks:
                t.requester = _name(msg)
                if not queue.current and first_track is None:
                    first_track = t
                    queue.current = t
                else:
                    if queue.add(t):
                        added += 1

            if first_track:
                try:
                    await join_and_play(call_py, msg.chat.id, first_track)
                except RuntimeError as e:
                    await status.edit_text(f"❌ {e}")
                    queue.current = None
                    return

            await status.edit_text(
                S.PLAYLIST_ADDED.format(count=added + 1, req=_name(msg))
            )
            return

        # ── Single track ──────────────────────────────────────────────
        status = await _reply(msg, S.SEARCHING.format(query=query))
        track = await search_youtube(query)
        if not track:
            await status.edit_text(S.NO_RESULTS)
            return

        track.requester = _name(msg)
        queue = get_queue(msg.chat.id)

        if queue.current:
            added = queue.add(track)
            if not added:
                await status.edit_text(S.QUEUE_FULL)
                return
            await status.edit_text(
                S.ADDED_QUEUE.format(
                    title=track.title,
                    url=track.webpage_url,
                    dur=format_duration(track.duration),
                    pos=len(queue),
                    req=track.requester,
                )
            )
        else:
            queue.current = track
            try:
                await join_and_play(call_py, msg.chat.id, track)
            except RuntimeError as e:
                await status.edit_text(f"❌ {e}")
                queue.current = None
                return
            await status.edit_text(
                S.NOW_PLAYING.format(
                    title=track.title,
                    url=track.webpage_url,
                    dur=format_duration(track.duration),
                    req=track.requester,
                )
            )

    # ── /skip ──────────────────────────────────────────────────────────
    @app.on_message(filters.command(["skip", "s"]) & filters.group)
    async def skip_cmd(client: Client, msg: Message):
        if not await is_admin(client, msg):
            await _reply(msg, S.ADMIN_ONLY)
            return
        queue = get_queue(msg.chat.id)
        if not queue.current:
            await _reply(msg, S.NO_PLAYING)
            return
        skipped = queue.current.title
        next_track = await play_next(call_py, msg.chat.id)
        if next_track:
            await _reply(msg, S.SKIPPED.format(
                skipped=skipped,
                title=next_track.title,
                url=next_track.webpage_url,
                dur=format_duration(next_track.duration),
                req=next_track.requester,
            ))
        else:
            await _reply(msg, S.SKIPPED_EMPTY)

    # ── /stop ──────────────────────────────────────────────────────────
    @app.on_message(filters.command(["stop", "end"]) & filters.group)
    async def stop_cmd(client: Client, msg: Message):
        if not await is_admin(client, msg):
            await _reply(msg, S.ADMIN_ONLY)
            return
        await stop_player(call_py, msg.chat.id)
        await _reply(msg, S.STOPPED)

    # ── /pause ─────────────────────────────────────────────────────────
    @app.on_message(filters.command("pause") & filters.group)
    async def pause_cmd(client: Client, msg: Message):
        if not await is_admin(client, msg):
            await _reply(msg, S.ADMIN_ONLY)
            return
        try:
            await pause_player(call_py, msg.chat.id)
            await _reply(msg, S.PAUSED)
        except Exception as e:
            await _reply(msg, f"❌ {e}")

    # ── /resume ────────────────────────────────────────────────────────
    @app.on_message(filters.command("resume") & filters.group)
    async def resume_cmd(client: Client, msg: Message):
        if not await is_admin(client, msg):
            await _reply(msg, S.ADMIN_ONLY)
            return
        try:
            await resume_player(call_py, msg.chat.id)
            await _reply(msg, S.RESUMED)
        except Exception as e:
            await _reply(msg, f"❌ {e}")

    # ── /volume ────────────────────────────────────────────────────────
    @app.on_message(filters.command("volume") & filters.group)
    async def volume_cmd(client: Client, msg: Message):
        if not await is_admin(client, msg):
            await _reply(msg, S.ADMIN_ONLY)
            return
        if len(msg.command) < 2:
            await _reply(msg, S.VOLUME_USAGE)
            return
        try:
            vol = int(msg.command[1])
        except ValueError:
            await _reply(msg, S.VOLUME_USAGE)
            return
        if not 1 <= vol <= 200:
            await _reply(msg, S.VOLUME_INVALID)
            return
        try:
            await change_volume(call_py, msg.chat.id, vol)
            await _reply(msg, S.VOLUME_SET.format(vol=vol))
        except Exception as e:
            await _reply(msg, f"❌ {e}")

    # ── /queue ─────────────────────────────────────────────────────────
    @app.on_message(filters.command(["queue", "q"]) & filters.group)
    async def queue_cmd(_, msg: Message):
        queue = get_queue(msg.chat.id)
        if not queue.current and not len(queue):
            await _reply(msg, S.QUEUE_EMPTY)
            return
        lines = []
        if queue.current:
            dur = format_duration(queue.current.duration)
            lines.append(
                f"▶️ **Now:** [{queue.current.title}]({queue.current.webpage_url}) `{dur}`"
            )
        for i, t in enumerate(queue.list_tracks(), 1):
            dur = format_duration(t.duration)
            lines.append(f"  {i}. [{t.title}]({t.webpage_url}) `{dur}` — {t.requester}")
        if queue.loop:
            lines.append("\n🔁 Loop is **ON**")
        await _reply(msg, "\n".join(lines))

    # ── /np ────────────────────────────────────────────────────────────
    @app.on_message(filters.command(["np", "now"]) & filters.group)
    async def np_cmd(_, msg: Message):
        queue = get_queue(msg.chat.id)
        if not queue.current:
            await _reply(msg, S.NO_PLAYING)
            return
        t = queue.current
        await _reply(msg, S.NP.format(
            title=t.title, url=t.webpage_url,
            dur=format_duration(t.duration), req=t.requester
        ))

    # ── /loop ──────────────────────────────────────────────────────────
    @app.on_message(filters.command("loop") & filters.group)
    async def loop_cmd(client: Client, msg: Message):
        if not await is_admin(client, msg):
            await _reply(msg, S.ADMIN_ONLY)
            return
        queue = get_queue(msg.chat.id)
        queue.loop = not queue.loop
        await _reply(msg, S.LOOP_ON if queue.loop else S.LOOP_OFF)

    # ── /clear ─────────────────────────────────────────────────────────
    @app.on_message(filters.command("clear") & filters.group)
    async def clear_cmd(client: Client, msg: Message):
        if not await is_admin(client, msg):
            await _reply(msg, S.ADMIN_ONLY)
            return
        get_queue(msg.chat.id).clear()
        await _reply(msg, S.CLEARED)

    # ── /lyrics ────────────────────────────────────────────────────────
    @app.on_message(filters.command(["lyrics", "ly"]) & filters.group)
    async def lyrics_cmd(_, msg: Message):
        if not GENIUS_TOKEN:
            await _reply(msg, S.LYRICS_NO_TOKEN)
            return
        if len(msg.command) < 2:
            # Try currently playing track
            queue = get_queue(msg.chat.id)
            if not queue.current:
                await _reply(msg, "❌ Provide a song name: `/lyrics <song>`")
                return
            query = queue.current.title
        else:
            query = " ".join(msg.command[1:])

        status = await _reply(msg, S.LYRICS_SEARCHING)
        result = await fetch_lyrics(query, GENIUS_TOKEN)
        if not result:
            await status.edit_text(S.LYRICS_NOT_FOUND.format(query=query))
            return

        header = S.LYRICS_HEADER.format(title=result["title"], artist=result["artist"])
        chunks = chunk_lyrics(result["lyrics"])
        await status.edit_text(header + chunks[0], disable_web_page_preview=True)
        for chunk in chunks[1:]:
            await msg.reply_text(chunk, disable_web_page_preview=True)

    # ── /help ──────────────────────────────────────────────────────────
    @app.on_message(filters.command("help") & filters.group)
    async def help_cmd(_, msg: Message):
        await _reply(msg, S.HELP)

    # ── Auto-advance on stream end ─────────────────────────────────────
    @call_py.on_stream_end()
    async def on_stream_end(_, update: StreamAudioEnded):
        chat_id = update.chat_id
        queue = get_queue(chat_id)

        if queue.loop and queue.current:
            try:
                await join_and_play(call_py, chat_id, queue.current)
            except Exception as e:
                logger.error(f"Loop replay failed [{chat_id}]: {e}")
            return

        next_track = await play_next(call_py, chat_id)
        if next_track:
            try:
                await app.send_message(
                    chat_id,
                    S.NOW_PLAYING.format(
                        title=next_track.title,
                        url=next_track.webpage_url,
                        dur=format_duration(next_track.duration),
                        req=next_track.requester,
                    ),
                    disable_web_page_preview=True,
                )
            except Exception:
                pass
        else:
            try:
                await app.send_message(chat_id, S.VC_LEFT)
            except Exception:
                pass
