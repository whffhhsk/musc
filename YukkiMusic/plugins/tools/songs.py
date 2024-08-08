import os
import re
import requests
import yt_dlp
from youtube_search import YoutubeSearch
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from YukkiMusic import app
from config import SUPPORT_CHANNEL, Muntazer
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, ChatWriteForbidden

# دالة للتحقق من اشتراك المستخدم في القناة
async def must_join_channel(app, msg):
    if not Muntazer:
        return
    try:
        if msg.from_user is None:
            return
        
        try:
            await app.get_chat_member(Muntazer, msg.from_user.id)
        except UserNotParticipant:
            if Muntazer.isalpha():
                link = "https://t.me/" + Muntazer
            else:
                chat_info = await app.get_chat(Muntazer)
                link = chat_info.invite_link
            try:
                await msg.reply(
                    f"~︙عليك الأشتراك في قناة البوت \n~︙قناة البوت : @{Muntazer}.",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⦗ قناة البوت ⦘", url=link)]
                    ])
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"I'm not admin in the MUST_JOIN chat {Muntazer}!")


@app.on_message(filters.command(["يوت", "yt", "تنزيل", "بحث"]))
async def song(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    
    # تحقق من الاشتراك الإجباري
    await must_join_channel(app, message)

    m = await message.reply_text("⦗ جارِ البحث يرجى الانتضار ⦘", quote=True)

    query = " ".join(str(i) for i in message.command[1:])
    ydl_opts = {"format": "bestaudio[ext=m4a]", "quiet": True}

    try:
        # استخدم البحث لإيجاد الفيديو المطلوب
        results = YoutubeSearch(query, max_results=5).to_dict()
        if not results:
            raise Exception("- لايوجد بحث .")
        
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"{title}.jpg"
        # إزالة الأحرف غير الصحيحة من اسم الملف
        thumb_name = re.sub(r'[\\/*?:"<>|]', '', thumb_name)
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]

        # تحميل ملف الصوت
        audio_file = ''
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=False)
                audio_file = ydl.prepare_filename(info_dict)
                ydl.process_info(info_dict)

            rep = f"**• by :** {message.from_user.first_name if message.from_user else 'Freedom'} \n⎯ ⎯ ⎯ ⎯\n• ch : @{Muntazer} ."

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

            visit_butt = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text="⦗ Источник ⦘", url=SUPPORT_CHANNEL)],
                ]
            )
            # إرسال ملف الصوت إلى المستخدم
            await message.reply_audio(
                audio=audio_file,
                caption=rep,
                thumb=thumb_name,
                title=title,
                duration=dur,
                reply_markup=visit_butt,
            )

            await m.delete()

            # إزالة الملفات المؤقتة بعد التحميل
            try:
                if audio_file:
                    os.remove(audio_file)
                os.remove(thumb_name)
            except Exception as ex:
                error_message = f"- فشل في حذف الملفات المؤقتة. \n\n**السبب :** `{ex}`"
                await m.edit_text(error_message)

        except Exception as ex:
            error_message = f"- فشل في تحميل الفيديو من YouTube. \n\n**السبب :** `{ex}`"
            await m.edit_text(error_message)

    except Exception as ex:
        error_message = f"- فشل .\n\n**السبب :** `{ex}`"
        await m.edit_text(error_message)
