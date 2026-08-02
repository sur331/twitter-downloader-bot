import os
import re
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# إعداد التسجيل للمتابعة
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# توكن البوت الخاص بك من BotFather
TOKEN = '8989802980:AAEUVZmllSfsXgRfa2XgBwI1B_Re6ku7lvs'

# مجلد حفظ التنزيلات
DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً بك! أرسل لي رابط فيديو من أي منصة (تيك توك، إنستغرام، X/تويتر، يوتيوب...) وسأقوم بتحميله لك فوراً.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    # التحقق من أن النص يحتوي على رابط
    if not re.match(r'https?://[^\s]+', url):
        return

    msg = await update.message.reply_text("⏳ جاري معالجة الرابط وتحميل الفيديو...")

    # إعدادات yt-dlp الشاملة لمعظم المنصات
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        # متطلبات لتفادي الحظر من بعض المنصات مثل TikTok وInstagram
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }

    filename = None
    try:
        # تشغيل yt-dlp في المسار غير المتزامن لعدم تجميد البوت
        loop = asyncio.get_running_loop()
        def extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)

        filename = await loop.run_in_executor(None, extract)

        # التأكد من صحة امتداد الملف بعد الدمج
        if not os.path.exists(filename):
            base_filename = os.path.splitext(filename)[0]
            if os.path.exists(f"{base_filename}.mp4"):
                filename = f"{base_filename}.mp4"

        # إرسال الفيديو للمستخدم
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="✨ تم التحميل بنجاح!"
            )

    except Exception as e:
        logging.error(f"Error downloading {url}: {e}")
        await msg.edit_text("❌ تعذر تحميل الفيديو. أرجو التأكد من صحة الرابط أو أن الحساب ليس خاصاً.")
    
    finally:
        # حذف رسالة "جاري التحميل"
        try:
            await msg.delete()
        except Exception:
            pass

        # مسح الملف من السيرفر لتوفير المساحة
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception as e:
                logging.error(f"Error deleting file: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("... البوت يعمل الآن")
    app.run_polling()

if __name__ == '__main__':
    main()
