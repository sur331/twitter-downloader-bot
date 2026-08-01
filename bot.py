import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# إعداد السجلات
logging.basicConfig(level=logging.INFO)

# ضع التوكن الخاص بك هنا
BOT_TOKEN = "8989802980:AAEUVZmlLSfsXgRfa2XgBwIlB_Re6ku7lvs"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً بك! أرسل لي رابط فيديو من أي منصة (TikTok, Reels, Twitter, YouTube) وسأقوم بتحميله **بدون علامة مائية** وبحجم مناسب لتليجرام.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("❌ يرجى إرسال رابط صحيح يبتدئ بـ http أو https.")
        return

    status_msg = await update.message.reply_text("⏳ جاري استخراج الفيديو بدون علامة مائية ومراعاة الحجم...")

    # إعدادات yt-dlp لإزالة العلامة المائية وتقييد الحجم بـ 48 ميجابايت
    ydl_opts = {
        # 1. تحديد الحجم الأقصى لتفادي خطأ Request Entity Too Large
        'max_filesize': 48 * 1024 * 1024,
        'format': 'bestvideo[filesize<=48M]+bestaudio/best[filesize<=48M]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        
        # 2. إعدادات لمنع العلامة المائية وتخصيص السيرفرات المباشرة (مثل تيك توك)
        'extractor_args': {
            'tiktok': {
                'app_version': '1.1.9',
                'manifest_app_version': '1.1.9',
            }
        },
        
        # 3. ترويسات متصفح لتجاوز الحماية
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # التحقق من وجود الملف وحجمه
        if os.path.exists(filename):
            file_size_mb = os.path.getsize(filename) / (1024 * 1024)
            
            if file_size_mb > 49.5:
                await status_msg.edit_text("❌ عذراً، حجم الفيديو الأصلي يتجاوز الحد الأقصى المسموح للبوتات (50MB).")
                os.remove(filename)
                return

            with open(filename, 'rb') as vf:
                await update.message.reply_video(
                    video=vf,
                    caption=info.get('title', 'تم التحميل بدون علامة مائية بنجاح! 🎬')
                )
            
            # تنظيف السيرفر وحذف الملف
            os.remove(filename)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ لم يتم العثور على الملف بعد التنزيل.")

    except Exception as e:
        error_msg = str(e)
        if "File is larger than max_filesize" in error_msg:
            await status_msg.edit_text("❌ حجم هذا الفيديو يتجاوز حد الـ 50 ميجابايت الخاص بتليجرام.")
        else:
            await status_msg.edit_text(f"❌ حدث خطأ أثناء التنزيل:\n`{error_msg[:150]}`")

def main():
    os.makedirs('downloads', exist_ok=True)
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("🚀 البوت قيد التشغيل...")
    app.run_polling()

if __name__ == '__main__':
    main()
