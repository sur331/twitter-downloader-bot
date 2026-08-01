import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8989802980:AAEUVZmlLSfsXgRfa2XgBwIlB_Re6ku7lvs"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً بك! أرسل لي رابط فيديو من أي منصة (Snapchat, TikTok, Reels, Twitter) وسأقوم بتحميله **بدون علامة مائية**.")

# دالة مخصصة لتحميل فيديو سناب شات بدون علامة مائية
def download_snapchat_no_watermark(url, output_path):
    # استخدام API مجاني وسريع لاستخراج رابط سناب المباشر الصافي
    api_url = f"https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "url": url,
        "videoQuality": "720"
    }
    
    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code == 200:
        res_data = response.json()
        download_url = res_data.get("url")
        if download_url:
            # تنزيل الفيديو من الرابط المباشر
            video_res = requests.get(download_url, stream=True)
            with open(output_path, 'wb') as f:
                for chunk in video_res.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            return True
    return False

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("❌ يرجى إرسال رابط صحيح يبتدئ بـ http أو https.")
        return

    status_msg = await update.message.reply_text("⏳ جاري التحميل وإزالة العلامة المائية...")
    file_path = f"downloads/{update.message.message_id}.mp4"

    try:
        # 1. إذا كان الرابط من سناب شات (Snapchat)
        if "snapchat.com" in url or "snap.com" in url:
            success = download_snapchat_no_watermark(url, file_path)
            if not success:
                # محاولة بديلة عبر yt-dlp إذا فشل الـ API
                ydl_opts = {'outtmpl': file_path, 'quiet': True, 'max_filesize': 48 * 1024 * 1024}
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

        # 2. لبقية المنصات (TikTok, Instagram, Twitter, YouTube)
        else:
            ydl_opts = {
                'max_filesize': 48 * 1024 * 1024,
                'format': 'bestvideo[filesize<=48M]+bestaudio/best[filesize<=48M]/best',
                'outtmpl': file_path,
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {
                    'tiktok': {
                        'app_version': '1.1.9',
                        'manifest_app_version': '1.1.9',
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                },
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        # التحقق من الملف وإرساله
        if os.path.exists(file_path):
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            if file_size_mb > 49.5:
                await status_msg.edit_text("❌ حجم الفيديو يتجاوز 50 ميجابايت (حد تليجرام الأقصى).")
                os.remove(file_path)
                return

            with open(file_path, 'rb') as vf:
                await update.message.reply_video(
                    video=vf,
                    caption="تم التحميل بدون علامة مائية بنجاح! 🎬"
                )
            
            os.remove(file_path)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ تعذر استخراج الفيديو بدون علامة مائية.")

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        await status_msg.edit_text(f"❌ حدث خطأ أثناء التنزيل:\n`{str(e)[:150]}`")

def main():
    os.makedirs('downloads', exist_ok=True)
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("🚀 البوت قيد التشغيل...")
    app.run_polling()

if __name__ == '__main__':
    main()
