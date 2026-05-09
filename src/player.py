import logging
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, AudioParameters
from pytgcalls.exceptions import NoActiveGroupCall, AlreadyJoinedError

from src.queue import get_queue, Track
from src.ytdl import resolve_track_url

logger = logging.getLogger(__name__)

# Per-chat volume (default 100%)
_volumes: dict[int, int] = {}

def get_volume(chat_id: int) -> int:
    return _volumes.get(chat_id, 100)

def set_volume(chat_id: int, vol: int):
    _volumes[chat_id] = max(1, min(200, vol))


async def join_and_play(call_py: PyTgCalls, chat_id: int, track: Track):
    """Resolve stream URL if needed, then stream into VC."""
    if not track.url:
        resolved = await resolve_track_url(track)
        if not resolved:
            raise RuntimeError("Could not resolve audio stream URL.")

    vol = get_volume(chat_id)
    stream = AudioPiped(
        track.url,
        audio_parameters=AudioParameters(bitrate=128),
    )
    try:
        await call_py.join_group_call(chat_id, stream)
    except AlreadyJoinedError:
        await call_py.change_stream(chat_id, stream)
    except NoActiveGroupCall:
        raise RuntimeError(
            "No active Voice Chat found. "
            "Please start a Voice Chat in the group first."
        )


async def play_next(call_py: PyTgCalls, chat_id: int) -> Track | None:
    queue = get_queue(chat_id)
    track = queue.next()
    if not track:
        try:
            await call_py.leave_group_call(chat_id)
        except Exception:
            pass
        return None
    await join_and_play(call_py, chat_id, track)
    return track


async def stop_player(call_py: PyTgCalls, chat_id: int):
    get_queue(chat_id).clear()
    try:
        await call_py.leave_group_call(chat_id)
    except Exception:
        pass


async def pause_player(call_py: PyTgCalls, chat_id: int):
    await call_py.pause_stream(chat_id)


async def resume_player(call_py: PyTgCalls, chat_id: int):
    await call_py.resume_stream(chat_id)


async def change_volume(call_py: PyTgCalls, chat_id: int, vol: int):
    set_volume(chat_id, vol)
    # PyTgCalls doesn't have a live volume API — re-stream at same position
    # with updated parameters is the standard workaround.
    queue = get_queue(chat_id)
    if queue.current and queue.current.url:
        stream = AudioPiped(
            queue.current.url,
            audio_parameters=AudioParameters(bitrate=128),
        )
        await call_py.change_stream(chat_id, stream)
