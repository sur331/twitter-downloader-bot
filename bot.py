import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# إعداد السجلات لمتابعة الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ضع توكن البوت الخاص بك هنا
BOT_TOKEN = "8859717725:AAFt9FWRA5kkmzZSNsUjQ1qv79l9kSR4i4Q"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل لي رابط فيديو من منصة X (تويتر) وسأقوم بتحميله لك فوراً.")

async def download_twitter_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not ("twitter.com" in url or "x.com" in url):
        await update.message.reply_text("عذراً، يرجى إرسال رابط صحيح من منصة X (تويتر).")
        return

    msg = await update.message.reply_text("جارٍ تحميل الفيديو... انتظر لحظة ⏳")
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(filename, 'rb'), caption="تم التحميل بنجاح! 🎬")
        
        os.remove(filename)
        await msg.delete()

    except Exception as e:
        logging.error(f"Error: {e}")
        await msg.edit_text("حدث خطأ أثناء تحميل الفيديو. تأكد من أن الحساب غير خاص أو أن الرابط يحتوي على فيديو.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_twitter_video))

    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    main()
