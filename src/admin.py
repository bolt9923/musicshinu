from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from config.settings import OWNER_ID


async def is_admin(client: Client, msg: Message) -> bool:
    """Return True if the sender is the bot owner OR a group admin/creator."""
    if msg.from_user and msg.from_user.id == OWNER_ID:
        return True
    try:
        member = await client.get_chat_member(msg.chat.id, msg.from_user.id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False
