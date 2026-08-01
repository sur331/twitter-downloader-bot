import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8989802980:AAEUVZmlLSfsXgRfa2XgBwIlB_Re6ku7lvs")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! 👋 أرسل لي رابط فيديو من (X/Twitter, Instagram, YouTube, TikTok, إلخ) وسأقوم بتحميله لك.")

async def handle_media_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    status_msg = await update.message.reply_text("⏳ جاري استخراج الفيديو وتحميله...")

    # إعدادات yt-dlp المعززة لدعم تويتر (X) وكافة المنصات
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        # إضافة User-Agent لضمان تجاوز حظر وتغييرات روابط تويتر/X
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            video_file = f"{base}.mp4" if os.path.exists(f"{base}.mp4") else filename

        with open(video_file, 'rb') as vf:
            await update.message.reply_video(
                video=vf,
                caption=info.get('title', 'تم التحميل بنجاح!')
            )

        if os.path.exists(video_file):
            os.remove(video_file)

        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        await status_msg.edit_text("❌ عذراً، تعذر تحميل الفيديو. تأكد من أن الحساب غير خاص وأن الرابط صحيح.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_media_download))
    app.run_polling()

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    main()
