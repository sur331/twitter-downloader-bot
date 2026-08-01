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

# ضع التوكن الخاص ببوتك هنا
BOT_TOKEN = "8989802980:AAEUVZmlLSfsXgRfa2XgBwIlB_Re6ku7lvs"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك!\nأرسل لي رابط أي تغريدة تحتوي على فيديو من منصة **X (تويتر)** وسأقوم بتحميله لك فوراً."
    )

async def download_x_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    # 1. التحقق من أن الرابط يتبع منصة X أو Twitter
    if not ("twitter.com" in url or "x.com" in url):
        await update.message.reply_text("❌ يرجى إرسال رابط صحيح من منصة X (تويتر).")
        return

    status_msg = await update.message.reply_text("⏳ جاري استخراج الفيديو من X وتحميله...")
    output_filename = f"downloads/{update.message.message_id}.mp4"

    # 2. إعدادات yt-dlp المخصصة لمنصة X
    ydl_opts = {
        # تحديد الحجم الأقصى لضمان عدم تجاوز 50MB (حد تليجرام)
        'max_filesize': 48 * 1024 * 1024,
        # اختيار أفضل جودة فيديو وصوت مدمجين بصيغة MP4
        'format': 'bestvideo[ext=mp4][filesize<=48M]+bestaudio[ext=m4a]/best[ext=mp4][filesize<=48M]/best',
        'outtmpl': output_filename,
        'quiet': True,
        'no_warnings': True,
        # ترويسة متصفح حديث لتجاوز الحماية وقراءة روابط x.com
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        },
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            caption_text = info.get('title', 'تم التحميل من منصة X بنجاح! 𝕏')

        # 3. التحقق من تنزيل الملف وإرساله
        if os.path.exists(output_filename):
            file_size_mb = os.path.getsize(output_filename) / (1024 * 1024)

            if file_size_mb > 49.5:
                await status_msg.edit_text("❌ حجم الفيديو كبير ويتجاوز حد الـ 50 ميجابايت المسموح للبوتات.")
                os.remove(output_filename)
                return

            with open(output_filename, 'rb') as vf:
                await update.message.reply_video(
                    video=vf,
                    caption=caption_text[:1024]  # حد أقصى لنص الوصف في تليجرام
                )
            
            # حذف الملف بعد الإرسال للحفاظ على المساحة
            os.remove(output_filename)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ تعذر العثور على الفيديو. قد تكون التغريدة بحساب خاص أو لا تحتوي فيديو.")

    except Exception as e:
        if os.path.exists(output_filename):
            os.remove(output_filename)
            
        err_msg = str(e)
        if "File is larger than max_filesize" in err_msg:
            await status_msg.edit_text("❌ الفيديو يتجاوز حد الـ 50MB الخاص بتليجرام.")
        else:
            await status_msg.edit_text(f"❌ حدث خطأ أثناء التنزيل من X:\n`تأكد أن الحساب ليس خاصاً وأن التغريدة تحتوي فيديو.`")

def main():
    os.makedirs('downloads', exist_ok=True)
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    # استقبال النصوص والروابط
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_x_video))
    
    print("🚀 بوت التحميل من X (تويتر) قيد التشغيل...")
    app.run_polling()

if __name__ == '__main__':
    main()
