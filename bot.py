import os
import logging
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from yt_dlp import YoutubeDL

# إعداد السجلات لمتابعة الأخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# لجلب التوكن من متغيرات البيئة (أفضل أماناً)، أو استخدم التوكن المباشر
BOT_TOKEN = os.getenv("BOT_TOKEN", "8989802980:AAEUVZmlLSfsXgRfa2XgBwIlB_Re6ku7lvs")

# دالة الترحب عند بدء التشغيل
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك! 👋\n\nأرسل لي أي رابط تغريدة تحتوي على **فيديو** أو **صور** من منصة X (تويتر)، وسأقوم بتحميلها لك فوراً."
    )

# دالة المعالجة والتحميل
async def handle_twitter_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # التحقق من صحة الرابط
    if not ("twitter.com" in url or "x.com" in url):
        await update.message.reply_text("❌ الرجاء إرسال رابط صحيح من منصة X (تويتر).")
        return

    status_msg = await update.message.reply_text("جاري جلب المحتوى... انتظر لحظة ⏳")

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # إعدادات yt-dlp المرنة للتعامل مع الفيديو والصور
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s_%(autonumber)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    downloaded_files = []

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # استخراج معلومات التغريدة
            info = ydl.extract_info(url, download=True)

            # معالجة المنشورات القائمة على قائمة (مثل ألبوم الصور)
            if 'entries' in info:
                entries = info['entries']
            else:
                entries = [info]

            for entry in entries:
                filename = ydl.prepare_filename(entry)
                if os.path.exists(filename):
                    downloaded_files.append(filename)

        if not downloaded_files:
            await status_msg.edit_text("❌ لم يتم العثور على وسائط قابلة للتحميل في هذا الرابط.")
            return

        # التفريق بين الصور والفيديوهات وإرسالها للمستخدم
        photos_to_send = []
        for file_path in downloaded_files:
            ext = file_path.split('.')[-1].lower()
            
            # إذا كان المحتوى فيديو
            if ext in ['mp4', 'mkv', 'mov', 'webm']:
                with open(file_path, 'rb') as video:
                    await update.message.reply_video(video=video, caption="تم تحميل الفيديو بنجاح! 🎬")
            
            # إذا كان المحتوى صورة
            elif ext in ['jpg', 'jpeg', 'png', 'webp']:
                photos_to_send.append(file_path)

        # إرسال الصور (كمجموعة ألبوم إن كانت أكثر من صورة)
        if photos_to_send:
            if len(photos_to_send) == 1:
                with open(photos_to_send[0], 'rb') as photo:
                    await update.message.reply_photo(photo=photo, caption="تم تحميل الصورة بنجاح! 📸")
            else:
                media_group = []
                files_handles = []
                for path in photos_to_send:
                    f = open(path, 'rb')
                    files_handles.append(f)
                    media_group.append(InputMediaPhoto(media=f))
                
                await update.message.reply_media_group(media=media_group)
                
                # إغلاق الملفات المفتوحة
                for f in files_handles:
                    f.close()

        # حذف الرسالة المؤقتة "جاري التحميل"
        await status_msg.delete()

    except Exception as e:
        logging.error(f"حدث خطأ أثناء التنزيل: {e}")
        await status_msg.edit_text("❌ حدث خطأ أثناء التحميل. تأكد من أن التغريدة تحتوي على وسائط وأن الحساب ليس خاصاً.")

    finally:
        # التنظيف الذاتي: حذف جميع الملفات المحملة بعد الإرسال للحفاظ على مساحة السيرفر
        for file_path in downloaded_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass

# التشغيل الرئيسي
if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_twitter_media))

    print("البوت يعمل بنجاح الآن...")
    app.run_polling()
