import os
import logging
import traceback
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# إعداد توكن البوت
BOT_TOKEN = "8989802980:AAEUVZmlLSfsXgRfa2XgBwIlB_Re6ku7lvs"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 البوت يعمل! أرسل رابط الفيديو الآن.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    status_msg = await update.message.reply_text("⏳ جاري التحميل...")

    # إعدادات بسيطة جداً وتعتمد على روابط متوافقة ومباشرة
    ydl_opts = {
        'format': 'best', # اختيار أفضل صيغة جاهزة مباشرة (فيديو + صوت)
        'outtmpl': 'video.%(ext)s',
        'overwrites': True,
        'quiet': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.exists(filename):
            with open(filename, 'rb') as vf:
                await update.message.reply_video(video=vf, caption="✅ تم التحميل!")
            os.remove(filename)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ لم يتم العثور على الملف بعد التنزيل.")

    except Exception as e:
        # إرسال نص الخطأ كاملاً للتعرف على المشكلة
        error_details = str(e)
        await status_msg.edit_text(f"❌ حدث خطأ:\n`{error_details[:300]}`", parse_mode='Markdown')

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("🚀 البوت قيد التشغيل...")
    app.run_polling()

if __name__ == '__main__':
    main()
