import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8989802980:AAEUVZmlLSfsXgRfa2XgBwIlB_Re6ku7lvs")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! 👋 أرسل لي رابط فيديو من أي منصة (X/Twitter, Instagram, YouTube, TikTok) وسأقوم بتحميله.")

async def handle_media_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    # التأكد من أن النص المرسل يحتوي على رابط
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("❌ يرجى إرسال رابط صحيح يبتدئ بـ http أو https.")
        return

    status_msg = await update.message.reply_text("⏳ جاري استخراج الفيديو وتحميله...")

    # إعدادات yt-dlp مبسطة لتفادي مشاكل FFmpeg والتحويلات
    ydl_opts = {
        # اختيار صيغة جاهزة مسبقاً (فيديو مع صوت) لتجنب الحاجة للدمج عبر ffmpeg
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        # إضافة الترويسات لمنع التظليل من تويتر وانستغرام
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # التأكد من وجود الملف ثم إرساله
        if os.path.exists(filename):
            with open(filename, 'rb') as vf:
                await update.message.reply_video(
                    video=vf,
                    caption=info.get('title', 'تم التحميل بنجاح!')
                )
            # مسح الملف فور الإرسال
            os.remove(filename)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ تعذر إيجاد ملف الفيديو بعد التحميل.")

    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        await status_msg.edit_text(f"❌ حدث خطأ أثناء التنزيل. قد يكون الحساب خاصاً أو الرابط غير مدعوم.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_media_download))
    
    app.run_polling()

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    main()
