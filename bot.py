async def download_twitter_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not ("twitter.com" in url or "x.com" in url):
        await update.message.reply_text("الرجاء إرسال رابط صحيح من منصة X")
        return

    msg = await update.message.reply_text("جاري تحميل الفيديو... انتظر لحظة")

    # إعدادات yt-dlp المحسّنة لتفادي مشاكل الدمج والتنسيق
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # إرسال الفيديو للمستخدم
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video)

        # حذف الملف بعد الإرسال لتوفير المساحة
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("حدث خطأ أثناء تحميل الفيديو، تأكد من أن الحساب ليس خاصاً.")
