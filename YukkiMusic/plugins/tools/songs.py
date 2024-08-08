import os
import re
import yt_dlp
from pyrogram import enums, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaVideo,
    Message,
)
from config import BANNED_USERS, SONG_DOWNLOAD_DURATION, SONG_DOWNLOAD_DURATION_LIMIT
from strings import get_command
from YukkiMusic import YouTube, app
from YukkiMusic.utils.decorators.language import language, languageCB
from YukkiMusic.utils.formatters import convert_bytes
from YukkiMusic.utils.inline.song import song_markup

# Commands
SONG_COMMAND = get_command("SONG_COMMAND")
YOUTUBE_COMMAND = "يوت"  # Define new command for YouTube

@app.on_message(filters.command(YOUTUBE_COMMAND) & filters.group & ~BANNED_USERS)
@language
async def youtube_command_group(client, message: Message, _):

    query = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else None
    if not query:
        return await message.reply_text("يرجى تقديم اسم الأغنية بعد الأمر.")

    # Notify that the download has started
    mystic = await message.reply_text("جاري تحميل الأغنية...")

    # Download the song
    yt_url = f"https://www.youtube.com/results?search_query={query}"
    with yt_dlp.YoutubeDL({"quiet": True}) as ytdl:
        x = ytdl.extract_info(yt_url, download=False)
    
    if "entries" in x:
        x = x["entries"][0]  # Take the first result

    title = (x["title"]).title()
    title = re.sub("\W+", " ", title)
    duration = x["duration"]

    # Choose the best audio format available
    formats = [f for f in x.get("formats", []) if "audio" in f["format"]]
    if not formats:
        return await mystic.edit_text("لم يتم العثور على صيغة صوتية مناسبة.")

    best_format = max(formats, key=lambda f: f.get("filesize", 0))
    format_id = best_format["format_id"]
    
    try:
        filename = await YouTube.download(
            yt_url,
            mystic,
            songaudio=True,
            format_id=format_id,
            title=title,
        )
    except Exception as e:
        return await mystic.edit_text(f"حدث خطأ أثناء تحميل الصوت: {str(e)}")

    # Send the audio file
    med = InputMediaAudio(
        media=filename,
        caption=title,
        title=title,
        performer=x.get("uploader", "Unknown"),
    )

    await mystic.edit_text("جاري إرسال الأغنية...")
    await app.send_chat_action(
        chat_id=message.chat.id,
        action=enums.ChatAction.UPLOAD_AUDIO,
    )

    try:
        await message.reply_audio(media=med)
    except Exception as e:
        print(e)
        return await mystic.edit_text(f"حدث خطأ أثناء إرسال الأغنية: {str(e)}")

    os.remove(filename)
