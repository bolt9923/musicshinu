from collections import deque
from dataclasses import dataclass
from typing import Optional
from config.settings import MAX_QUEUE_SIZE


@dataclass
class Track:
    title: str
    url: str           # direct audio stream URL
    webpage_url: str   # original YouTube URL
    duration: int      # seconds
    requester: str     # display name of requester


class MusicQueue:
    def __init__(self):
        self._queue: deque[Track] = deque()
        self.current: Optional[Track] = None
        self.loop: bool = False

    def add(self, track: Track) -> bool:
        if len(self._queue) >= MAX_QUEUE_SIZE:
            return False
        self._queue.append(track)
        return True

    def next(self) -> Optional[Track]:
        if self.loop and self.current:
            return self.current
        if self._queue:
            self.current = self._queue.popleft()
            return self.current
        self.current = None
        return None

    def skip(self) -> Optional[Track]:
        if self._queue:
            self.current = self._queue.popleft()
            return self.current
        self.current = None
        return None

    def clear(self):
        self._queue.clear()
        self.current = None

    def list_tracks(self) -> list[Track]:
        return list(self._queue)

    def __len__(self):
        return len(self._queue)


_queues: dict[int, MusicQueue] = {}

def get_queue(chat_id: int) -> MusicQueue:
    if chat_id not in _queues:
        _queues[chat_id] = MusicQueue()
    return _queues[chat_id]
