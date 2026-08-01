import os
import re
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# إعداد التسجيل للمتابعة
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# توكن البوت الخاص بك من BotFather
TOKEN = '8989802980:AAEUVZmlLSfsXgRfa2XgBwIlB_Re6ku7lvs'

# الدالة الخاصة بأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً بك! أرسل لي رابط تغريدة تحتوي على فيديو وسأقوم بتحميله لك فوراً.")

# الدالة الأساسية لمعالجة الروابط وتنزيل الفيديو
async def download_twitter_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # التحقق من أن الرابط يخص منصة X / Twitter
    if not re.search(r'https?://(www\.)?(twitter|x)\.com/\w+/status/\d+', url):
        return

    msg = await update.message.reply_text("⏳ جاري جلب الفيديو، انتظر لحظة...")

    # إعدادات مكتبة yt-dlp للحصول على أعلى جودة فيديو
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # إرسال الفيديو للمستخدم
        await update.message.reply_video(
            video=open(filename, 'rb'),
            caption="✨ تم التنزيل بنجاح!"
        )

        # مسح الملف من السيرفر بعد الإرسال لتوفير المساحة
        if os.path.exists(filename):
            os.remove(filename)

        await msg.delete()

    except Exception as e:
        await msg.edit_text("❌ تعذر العثور على الفيديو. قد تكون التغريدة بحساب خاص أو لا تحتوي على فيديو مباشر.")
        print(f"Error: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_twitter_video))

    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    main()
