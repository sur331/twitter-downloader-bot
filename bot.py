import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

logging.basicConfig(level=logging.INFO)

# ضع التوكن الخاص بك هنا
BOT_TOKEN = "8989802980:AAEUVZmlLSfsXgRfa2XgBwIlB_Re6ku7lvs"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك!\nأرسل لي رابط فيديو من (TikTok, Instagram, Twitter, Snapchat, YouTube) وسأقوم بتحميله بحجم مناسب لتليجرام وبأفضل جودة متاحة."
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("❌ يرجى إرسال رابط صحيح يبدأ بـ http أو https.")
        return

    status_msg = await update.message.reply_text("⏳ جاري استخراج الفيديو وتحميله...")
    output_filename = f"downloads/{update.message.message_id}.mp4"

    # إعدادات yt-dlp المتوافقة مع سكريبتات GitHub المنشورة للبوتات
    ydl_opts = {
        # تحديد حد الحجم الأقصى لتفادي خطأ Request Entity Too Large
        'max_filesize': 48 * 1024 * 1024,
        'format': 'bestvideo[filesize<=48M][ext=mp4]+bestaudio[ext=m4a]/best[filesize<=48M][ext=mp4]/best[filesize<=48M]',
        'outtmpl': output_filename,
        'quiet': True,
        'no_warnings': True,
        # خيارات تجاوز الحظر وإزالة علامات تيك توك عبر السيرفرات المباشرة
        'extractor_args': {
            'tiktok': {
                'app_version': '1.1.9',
                'manifest_app_version': '1.1.9',
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # التأكد من الملف وحجمه قبل الإرسال لتليجرام
        if os.path.exists(output_filename):
            file_size_mb = os.path.getsize(output_filename) / (1024 * 1024)

            if file_size_mb > 49.5:
                await status_msg.edit_text("❌ عذراً، حجم الفيديو يتجاوز حد الـ 50 ميجابايت المسموح للبوتات في تليجرام.")
                os.remove(output_filename)
                return

            with open(output_filename, 'rb') as vf:
                await update.message.reply_video(
                    video=vf,
                    caption=f"✅ تم التحميل بنجاح!\n📌 المصدر: {info.get('extractor_key', 'مباشر')}"
                )
            
            # تنظيف السيرفر
            os.remove(output_filename)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ تعذر العثور على ملف الفيديو بعد التنزيل.")

    except Exception as e:
        if os.path.exists(output_filename):
            os.remove(output_filename)
            
        err_text = str(e)
        if "File is larger than max_filesize" in err_text:
            await status_msg.edit_text("❌ الفيديو كبير جداً ويتجاوز حد الـ 50MB الخاص بتليجرام.")
        else:
            await status_msg.edit_text(f"❌ حدث خطأ أثناء التحميل:\n`{err_text[:150]}`")

def main():
    os.makedirs('downloads', exist_ok=True)
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("🚀 البوت يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == '__main__':
    main()
