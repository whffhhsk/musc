from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from youtube_search import YoutubeSearch as B3KKK 
import requests
import yt_dlp
import os
from YukkiMusic import app

@app.on_message(filters.command("يوت"))
async def search(client: Client, m: Message):
    AssId = m.from_user.id
    try:
        Msg = m.text.split(None, 1)[1]
    except IndexError:
        return await m.reply("يرجى كتابة اسم الأغنية بعد الأمر.")
        
    B3 = B3KKK(Msg, max_results=4).to_dict()
    buttons = []
    for i in B3:
        buttons.append([
            InlineKeyboardButton(i["title"], callback_data=f"{AssId}Down{i['id']}")
        ])
    
    await m.reply(
        f"-› نتائج بحثك عن {Msg}:",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query(filters.regex("Down"))
async def get_info(client: Client, query: CallbackQuery):
    AssId = query.data.split("Down")[0]
    IdVi = query.data.split("Down")[1]
    if not query.from_user.id == int(AssId):
        return await query.answer("هذا الأمر لا يخصك ", show_alert=True)
    
    await query.message.delete()
    B3 = B3KKK(f'https://youtu.be/{IdVi}', max_results=1).to_dict()
    title = B3[0]['title']
    url = f'https://youtu.be/{IdVi}'
    
    await client.send_message(
        query.message.chat.id,
        f"[{title}]({url})",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("صوت", callback_data=f'{AssId}MuAu{IdVi}')],
            [InlineKeyboardButton("🧚‍♀", user_id=5565674333)],
        ])
    )

@app.on_callback_query(filters.regex("MuAu"))
async def get_audio(client: Client, query: CallbackQuery):
    IdVi = query.data.split("MuAu")[1]
    AssId = query.data.split("MuAu")[0]
  
    if not query.from_user.id == int(AssId):
        return await query.answer("هذا الأمر لا يخصك ", show_alert=True)
      
    url = f'https://youtu.be/{IdVi}'
    await query.edit_message_text(
        "⏳ جاري التحميل ..", 
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏳", callback_data='none')]])
    )
      
    ydl_ops = {"format": "bestaudio[ext=m4a]"}
    with yt_dlp.YoutubeDL(ydl_ops) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        
    if int(info_dict['duration']) > 3605:
        return await query.edit_message_text(
            "حد التحميل ساعة فقط",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚠️", callback_data='none')]])
        )
      
    audio_file = ydl.prepare_filename(info_dict)
    ydl.process_info(info_dict)
    await query.edit_message_text(
        "جاري الإرسال ..",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀", callback_data='none')]])
    )
    
    response = requests.get(info_dict['thumbnail'])
    with open(f"{IdVi}.png", "wb") as file:
        file.write(response.content)
      
    user = await client.get_users(int(AssId))
    await query.message.reply_audio(
        audio_file,
        title=info_dict['title'],
        duration=int(info_dict['duration']),
        performer=info_dict['channel'],
        caption=f'• من طلب -› {user.mention}',
        thumb=f"{IdVi}.png"
    )
      
    await query.edit_message_text(
        f"🔗 [{info_dict['title']}]({url})",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Owner", user_id=5565674333)]]),
        disable_web_page_preview=True
    )
    
    os.remove(f"{IdVi}.png")
    os.remove(audio_file)
