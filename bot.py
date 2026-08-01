import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# إعداد السجلات لمعرفة المشكلة فوراً من الـ Terminal
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8989802980:AAEUVZmlLSfsXgRfa2XgBwIlB_Re6ku7lvs"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 البوت متصل ويعمل! أرسل رابط الفيديو الآن.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    status_msg = await update.message.reply_text("⏳ جاري التحميل...")

    # خيارات بسيطة بدون شروط معقدة لتفادي التوقف
    ydl_opts = {
        'format': 'b',  # اختيار أسرع وأبسط صيغة مباشرة
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': False,  # إظهار التفاصيل في الـ terminal للمتابعة
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.exists(filename):
            with open(filename, 'rb') as vf:
                await update.message.reply_video(video=vf, caption="✅ تم التنزيل")
            os.remove(filename)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ لم يتم العثور على الملف بعد التنزيل.")

    except Exception as e:
        print(f"Error details: {e}")  # طباعة الخطأ كاملاً في الـ Terminal
        await status_msg.edit_text(f"❌ حدث خطأ أثناء التنزيل.\nالتفاصيل: {str(e)[:150]}")

def main():
    os.makedirs('downloads', exist_ok=True)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("🚀 البوت قيد التشغيل...")
    app.run_polling()

if __name__ == '__main__':
    main()
