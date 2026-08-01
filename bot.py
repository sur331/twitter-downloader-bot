import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from yt_dlp import YoutubeDL

# إعداد السجلات لمتابعة الأخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ⚠️ تنبيه: يفضل عدم كتابة التوكن هنا مباشرة ونقله لمتغيرات البيئة (Environment Variables)
BOT_TOKEN = "8989802980:AAEUVZmlLSfsXgRfa2XgBwIlB_Re6ku7lvs"

# دالة الترحيب عند كتابة /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل لي رابط فيديو من منصة X (تويتر) وسأقوم بتحميله لك.")

# دالة تحميل الفيديو
async def download_twitter_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # التأكد من أن الرابط يتبع منصة تويتر/X
    if not ("twitter.com" in url or "x.com" in url):
        await update.message.reply_text("الرجاء إرسال رابط صحيح من منصة X (تويتر).")
        return

    msg = await update.message.reply_text("جاري تحميل الفيديو... انتظر لحظة ⏳")

    # إنشاء مجلد للتنزيلات المؤقتة إذا لم يكن موجوداً
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # إعدادات yt-dlp المتوافقة
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        # تحميل الفيديو
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # إرسال الفيديو للمستخدم
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption="تم التحميل بنجاح! 🎬")

        # مسح رسالة "جاري التحميل"
        await msg.delete()

        # حذف الملف بعد الإرسال لتوفير المساحة على السيرفر
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        await update.message.reply_text("حدث خطأ أثناء تحميل الفيديو. تأكد من أن الرابط يحتوي على فيديو وأن الحساب ليس خاصاً.")

# تشغيل البوت
if __name__ == '__main__':
    # بناء التطبيق
    app = Application.builder().token(BOT_TOKEN).build()

    # تسجيل المشغلات (Handlers)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_twitter_video))

    # بدء تشغيل البوت
    print("Bot is running...")
    app.run_polling()
