import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import yt_dlp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# =========================================================
# 1. السيرفر الوهمي لتجاوز مشكلة المنفذ (Port) في Render
# =========================================================


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b'Bot is running successfully!')


def run_dummy_server():
  port = int(os.environ.get('PORT', 8080))
  server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
  server.serve_forever()


# تشغيل السيرفر في الخلفية عند بدء التشغيل
Thread(target=run_dummy_server, daemon=True).start()

# =========================================================
# 2. إعدادات البوت واللوج
# =========================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

# ضع توكن البوت الخاص بك هنا (بين التنصيص) أو استخدم Environment Variable باسم BOT_TOKEN
TELEGRAM_BOT_TOKEN = os.environ.get(
    'BOT_TOKEN', '8989802980:AAEUVZmlLSfsXgRfa2XgBwIlB_Re6ku7lvs'
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """أمر البداية /start"""
  await update.message.reply_text(
      'أهلاً بك! 👋\nأرسل لي رابط فيديو من (تيك توك، إنستغرام، يوتيوب،'
      ' تويتر...) وسأقوم بتحميله لك فوراً.'
  )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """معالجة الرابط المباشر وتحميل الفيديو"""
  url = update.message.text.strip()

  if not url.startswith(('http://', 'https://')):
    await update.message.reply_text('من فضلك أرسل رابطاً صحيحاً للفيديو.')
    return

  msg = await update.message.reply_text('جاري جلب وتحميل الفيديو... ⏳')
  output_filename = f'video_{update.message.message_id}.mp4'

  # إعدادات التحميل عبر yt-dlp
  ydl_opts = {
      'format': (
          'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
      ),
      'outtmpl': output_filename,
      'quiet': True,
      'max_filesize': 50 * 1024 * 1024,  # الحد الأقصى 50 ميجابايت
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([url])

    # إرسال الفيديو للمستخدم
    await update.message.reply_video(
        video=open(output_filename, 'rb'),
        caption='تم التحميل بنجاح! 🎬',
    )
    await msg.delete()

  except Exception as e:
    logging.error(f'Error: {e}')
    await msg.edit_text(
        'حدث خطأ أثناء تحميل الفيديو. تأكد من صحة الرابط وأن الحساب ليس خاصاً'
        ' (Private).'
    )

  finally:
    # تنظيف الملفات المؤقتة من السيرفر
    if os.path.exists(output_filename):
      os.remove(output_filename)


# =========================================================
# 3. تشغيل تطبيق البوت
# =========================================================
if __name__ == '__main__':
  app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

  app.add_handler(CommandHandler('start', start))
  app.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
  )

  print('Bot is polling...')
  app.run_polling()
