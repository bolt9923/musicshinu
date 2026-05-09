"""
All bot messages in English + Hindi.
Usage: from src.strings import S
       S.NOW_PLAYING.format(title=..., url=..., dur=..., req=...)
"""

class S:
    BOT_NAME = "🎵 Shinu Music Bot"

    # ── Playback ──────────────────────────────────────────────────────
    SEARCHING = "🔍 Searching for **{query}**…\n_खोजा जा रहा है…_"

    NOW_PLAYING = (
        "▶️ **Now Playing | अभी बज रहा है**\n"
        "🎵 [{title}]({url})\n"
        "⏱ `{dur}` | 👤 {req}"
    )

    ADDED_QUEUE = (
        "✅ **Added to Queue | Queue में जोड़ा**\n"
        "🎵 [{title}]({url})\n"
        "⏱ `{dur}` | 📌 #{pos} | 👤 {req}"
    )

    QUEUE_FULL = "❌ Queue is full! (50 max)\n_Queue भरी हुई है!_"
    NO_RESULTS = "❌ No results found. Try another search.\n_कोई परिणाम नहीं मिला।_"
    NO_VC      = "❌ No active Voice Chat found.\nGroup में **Voice Chat** शुरू करें, फिर `/play` करें।"
    NO_PLAYING = "❌ Nothing is playing right now.\n_अभी कुछ नहीं बज रहा।_"

    SKIPPED = (
        "⏭ **Skipped | स्किप किया**\n"
        "~~{skipped}~~\n\n"
        "▶️ **Now Playing | अभी बज रहा है**\n"
        "🎵 [{title}]({url})\n"
        "⏱ `{dur}` | 👤 {req}"
    )
    SKIPPED_EMPTY = "⏭ Skipped. Queue is empty, leaving VC.\n_Queue खाली है, VC छोड़ रहा हूँ।_"

    STOPPED   = "⏹ Stopped & queue cleared.\n_बंद कर दिया, queue साफ़ की।_"
    PAUSED    = "⏸ Paused.\n_रोका गया।_"
    RESUMED   = "▶️ Resumed.\n_फिर से शुरू।_"
    LOOP_ON   = "🔁 Loop mode **ON**.\n_लूप चालू।_"
    LOOP_OFF  = "🔁 Loop mode **OFF**.\n_लूप बंद।_"
    CLEARED   = "🗑 Queue cleared.\n_Queue साफ़ की गई।_"
    QUEUE_EMPTY = "📭 Queue is empty.\n_Queue खाली है।_"
    VC_LEFT   = "📭 Queue finished. Left the voice chat.\n_Queue खत्म, VC छोड़ दिया।_"

    # ── Volume ────────────────────────────────────────────────────────
    VOLUME_SET      = "🔊 Volume set to **{vol}%**\n_वॉल्यूम सेट किया: {vol}%_"
    VOLUME_INVALID  = "❌ Volume must be between 1 and 200.\n_Volume 1 से 200 के बीच होनी चाहिए।_"
    VOLUME_USAGE    = "❌ Usage: `/volume <1-200>`"

    # ── Playlist ──────────────────────────────────────────────────────
    PLAYLIST_LOADING = "📋 Loading playlist… | _प्लेलिस्ट लोड हो रही है…_"
    PLAYLIST_ADDED   = "📋 **Playlist added | प्लेलिस्ट जोड़ी**\n🎵 {count} tracks queued | 👤 {req}"
    PLAYLIST_EMPTY   = "❌ Playlist has no tracks or is private.\n_Playlist खाली है या private है।_"

    # ── Lyrics ────────────────────────────────────────────────────────
    LYRICS_SEARCHING = "🔍 Fetching lyrics… | _Lyrics ढूंढ रहे हैं…_"
    LYRICS_NOT_FOUND = "❌ Lyrics not found for **{query}**.\n_Lyrics नहीं मिले।_"
    LYRICS_NO_TOKEN  = "❌ Genius API token not configured.\nSet `GENIUS_TOKEN` in your `.env` file."
    LYRICS_HEADER    = "🎼 **{title}** — {artist}\n\n"

    # ── Admin guard ───────────────────────────────────────────────────
    ADMIN_ONLY = "🚫 Only group admins can use this command.\n_यह command सिर्फ admins के लिए है।_"

    # ── Now Playing (np) ──────────────────────────────────────────────
    NP = (
        "🎵 **Now Playing | अभी बज रहा है**\n"
        "[{title}]({url})\n"
        "⏱ `{dur}` | 👤 {req}"
    )

    # ── Help ──────────────────────────────────────────────────────────
    HELP = """
🎵 **Shinu Music Bot** — Commands

**Playback | प्लेबैक**
• `/play <song / URL>` — Play or queue a YouTube song
• `/play <playlist URL>` — Queue an entire YouTube playlist
• `/skip` — Skip current track _(admin only)_
• `/stop` — Stop & clear queue _(admin only)_
• `/pause` — Pause playback _(admin only)_
• `/resume` — Resume playback _(admin only)_
• `/volume <1-200>` — Set volume _(admin only)_

**Queue | Queue**
• `/queue` — Show current queue
• `/np` — Now playing info
• `/loop` — Toggle loop mode _(admin only)_
• `/clear` — Clear the queue _(admin only)_

**Extras | अन्य**
• `/lyrics <song name>` — Get song lyrics
• `/help` — Show this message

> ⚠️ An admin must **Start Voice Chat** in the group before using `/play`.
> ⚠️ Group में admin को पहले **Voice Chat** शुरू करना होगा।
"""
