"""
Run this script ONCE on your local PC to generate the STRING_SESSION.
Then add it to Heroku config vars.

Usage:
    pip install pyrogram TgCrypto
    python generate_session.py

It will ask for:
  - Your phone number (of the ASSISTANT account)
  - The OTP Telegram sends you
  - Your 2FA password (if enabled)

Then it prints your STRING_SESSION — copy it and run:
    heroku config:set STRING_SESSION=the_printed_string
"""

from pyrogram import Client
from config.settings import API_ID, API_HASH

print("=" * 60)
print("  Shinu Music Bot — Assistant Session Generator")
print("=" * 60)
print()
print("⚠️  Use a SECONDARY Telegram account, not your main one.")
print("    The assistant account will appear in Voice Chats.")
print()

with Client(
    ":memory:",
    api_id=API_ID,
    api_hash=API_HASH,
) as app:
    session = app.export_session_string()

print()
print("=" * 60)
print("✅  Your STRING_SESSION (copy everything below this line):")
print()
print(session)
print()
print("=" * 60)
print()
print("Now add it to Heroku:")
print(f'  heroku config:set STRING_SESSION="{session}"')
print()
print("Or paste it in Heroku Dashboard → Settings → Config Vars")
