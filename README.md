# 🎵 Shinu Music Bot

A feature-rich Telegram group music bot that streams YouTube audio directly into **Voice Chats (Live VC)**.

Built with [Pyrogram](https://pyrogram.org/) + [PyTgCalls](https://pytgcalls.github.io/).

---

## ✨ Features

| Feature | Details |
|---|---|
| ▶️ YouTube Playback | Search by name or paste any YouTube URL |
| 📋 Playlist Support | Queue entire YouTube playlists (up to 50 tracks) |
| 🔊 Volume Control | `/volume 1–200` |
| 🎼 Lyrics | `/lyrics` via Genius API |
| 🔁 Loop Mode | Replay current track |
| 🛡 Admin-only Controls | skip/stop/pause/resume/loop/clear — group admins only |
| 🌐 English + Hindi | Bilingual bot messages |
| 🚀 Railway / Heroku ready | One-click deploy configs included |

---

## 📋 Prerequisites

- Python **3.10+**
- **FFmpeg** on your system (`apt install ffmpeg`)
- Telegram **API ID & Hash** → [my.telegram.org](https://my.telegram.org/apps)
- **Bot Token** → [@BotFather](https://t.me/BotFather)
- _(Optional)_ **Genius Token** for `/lyrics` → [genius.com/api-clients](https://genius.com/api-clients)

> ⚠️ Bot must be a **group admin**, and a human admin must **Start Voice Chat** before `/play` works.

---

## 🚀 Deploy on Railway (Recommended)

1. Fork this repo to your GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Select your forked repo
4. Go to **Variables** tab and add:

| Variable | Value |
|---|---|
| `API_ID` | From my.telegram.org |
| `API_HASH` | From my.telegram.org |
| `BOT_TOKEN` | From @BotFather |
| `OWNER_ID` | `423346191` |
| `GENIUS_TOKEN` | From genius.com/api-clients (optional) |

5. Railway auto-detects `Dockerfile` and deploys. Done! ✅

---

## 🟣 Deploy on Heroku

```bash
# 1. Clone
git clone https://github.com/yourname/shinu-music-bot
cd shinu-music-bot

# 2. Login & create app
heroku login
heroku create shinu-music-bot

# 3. Add buildpack for ffmpeg
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
heroku buildpacks:add heroku/python

# 4. Set environment variables
heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set OWNER_ID=423346191
heroku config:set GENIUS_TOKEN=your_genius_token   # optional

# 5. Deploy
git push heroku main

# 6. Start worker dyno
heroku ps:scale worker=1
```

---

## 💻 Local Setup

```bash
git clone https://github.com/yourname/shinu-music-bot
cd shinu-music-bot
pip install -r requirements.txt
cp .env.example .env
# Fill in .env with your credentials
python bot.py
```

---

## 🐳 Docker

```bash
cp .env.example .env   # fill in credentials
docker build -t shinu-music-bot .
docker run --env-file .env shinu-music-bot
```

---

## 🤖 Commands

| Command | Description | Who |
|---|---|---|
| `/play <song or URL>` | Play / queue a track or playlist | Everyone |
| `/queue` | View current queue | Everyone |
| `/np` | Now playing info | Everyone |
| `/lyrics [song]` | Get song lyrics | Everyone |
| `/skip` | Skip current track | Admins |
| `/stop` | Stop & clear queue | Admins |
| `/pause` | Pause stream | Admins |
| `/resume` | Resume stream | Admins |
| `/volume <1-200>` | Set volume | Admins |
| `/loop` | Toggle loop mode | Admins |
| `/clear` | Clear queue | Admins |
| `/help` | Show help | Everyone |

---

## 🗂 Project Structure

```
shinu-music-bot/
├── bot.py                  # Entry point
├── config/
│   └── settings.py         # Env config & constants
├── src/
│   ├── handlers.py         # All command handlers + stream-end event
│   ├── player.py           # VC join/stream/skip/volume logic
│   ├── queue.py            # Per-chat MusicQueue data structure
│   ├── ytdl.py             # yt-dlp: search, single track, playlist
│   ├── lyrics.py           # Genius API lyrics fetcher
│   ├── admin.py            # Admin permission checker
│   └── strings.py          # All messages (English + Hindi)
├── Procfile                # Heroku/Railway worker
├── runtime.txt             # Python version pin
├── railway.toml            # Railway deploy config
├── app.json                # Heroku app manifest
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## ⚙️ How It Works

1. `/play <query>` → **yt-dlp** finds the best audio stream URL (no download, streams directly)
2. **PyTgCalls** pipes the URL into Telegram's Voice Chat via MTProto
3. `on_stream_end` fires when a track finishes → auto-plays the next queued track
4. Queue is empty → bot leaves the voice chat automatically

---

## 🛠 Troubleshooting

| Problem | Fix |
|---|---|
| `NoActiveGroupCall` | Start Voice Chat in group first (admin → ⋮ → Start Voice Chat) |
| `AuthKeyUnregistered` | Delete `*.session` files and restart |
| No audio / silence | Check `ffmpeg -version` — must be installed |
| Bot can't join VC | Ensure bot has **admin** rights in the group |
| `/lyrics` not working | Set `GENIUS_TOKEN` in your env variables |

---

## 📄 License

MIT — free to use and modify.
