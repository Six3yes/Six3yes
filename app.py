import os
import requests
import time
import json
from datetime import datetime
from flask import Flask, jsonify
import threading
import logging
import atexit

app = Flask(__name__)

# تنظیم لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("RUBIKA_TOKEN", "FBICI0TARGDLXTXZUBLYODAGLEPQXKRDDQPJWZDIHSVKSEDBOKBVVPCNWPUTILSF")
BASE_URL = f"https://botapi.rubika.ir/v3/{TOKEN}"

RESPONSES = {
    "start": """✨ **سلام عزیز! به ربات هوشمند Six3yes خوش آمدی!** ✨

👇 **برای شروع، یکی از گزینه‌های زیر را انتخاب کن:**
1️⃣ زمان‌بندی توسعه
2️⃣ ویژگی‌های آینده  
3️⃣ ارور کیست؟
4️⃣ مالک

💡 فقط عدد گزینه رو بفرست.""",
    "option1": """⏳ **زمان‌بندی دقیق ارائه ربات:**\n🔴 **تاریخ نهایی: یک ماه دیگر**""",
    "option2": """🤖 **ویژگی‌های ربات:**\n🛡️ مدیریت گروه\n🧠 هوش مصنوعی\n🎮 بازی‌ها\n🎵 ویس‌کال""",
    "option3": """⚠️ **هشدار!**\n😱 **ارور:** یک 'هکیر' خیالی!""",
    "option4": """👑 **مالک:**\n• **نام:** آرین\n• **شماره:** `+98 939 625 5842`"""
}

class Six3yesBot:
    def __init__(self):
        self.is_running = False
        self.polling_thread = None
        logger.info("🤖 شیء ربات Six3yes ساخته شد")
    
    def send_message(self, chat_id, text):
        try:
            payload = {"chat_id": chat_id, "text": text[:4000]}
            response = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ پیام ارسال شد به {chat_id[:8]}...")
                return True
            else:
                logger.error(f"❌ خطا در ارسال پیام: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ خطا در ارسال: {e}")
            return False
    
    def process_text(self, text):
        text = text.strip().lower()
        
        if text in ["/start", "استارت", "شروع", "start"]:
            return RESPONSES["start"]
        elif text in ["1", "گزینه 1", "زمان‌بندی", "زمانبندی"]:
            return RESPONSES["option1"]
        elif text in ["2", "گزینه 2", "ویژگی", "ویژگی ها"]:
            return RESPONSES["option2"]
        elif text in ["3", "گزینه 3", "ارور", "ارور کیست"]:
            return RESPONSES["option3"]
        elif text in ["4", "گزینه 4", "مالک", "سازنده"]:
            return RESPONSES["option4"]
        else:
            return "🤖 لطفاً عدد ۱ تا ۴ را انتخاب کنید یا /start را بزنید."
    
    def polling_loop(self):
        """حلقه اصلی دریافت پیام‌ها"""
        logger.info("📡 حلقه دریافت پیام‌ها (polling_loop) شروع شد")
        last_update_id = 0
        
        while self.is_running:
            try:
                payload = {"start_id": last_update_id} if last_update_id > 0 else {}
                response = requests.post(f"{BASE_URL}/getUpdates", json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "OK":
                        updates = data.get("data", {}).get("updates", [])
                        
                        for update in updates:
                            update_id = update.get("update_id", 0)
                            if update_id > last_update_id:
                                last_update_id = update_id
                                
                                if update.get("type") == "NewMessage":
                                    msg = update.get("new_message", {})
                                    text = msg.get("text", "").strip()
                                    chat_id = update.get("chat_id")
                                    
                                    if text and chat_id:
                                        logger.info(f"📩 پیام از {chat_id[:8]}...: {text[:30]}")
                                        reply = self.process_text(text)
                                        self.send_message(chat_id, reply)
                else:
                    logger.error(f"خطا از سرور روبیکا: {response.status_code}")
                
                time.sleep(2)  # تاخیر بین درخواست‌ها
                
            except requests.exceptions.RequestException as e:
                logger.error(f"خطای شبکه در polling: {e}")
                time.sleep(5)
            except Exception as e:
                logger.error(f"خطای غیرمنتظره در polling: {e}")
                time.sleep(5)
    
    def start_polling(self):
        """شروع دریافت پیام‌ها در یک ترد جداگانه"""
        if self.is_running:
            logger.warning("⚠️ ربات در حال حاضر در حال اجراست!")
            return
        
        self.is_running = True
        self.polling_thread = threading.Thread(target=self.polling_loop, daemon=True)
        self.polling_thread.start()
        logger.info("🚀 ربات شروع به کار کرد و در حال دریافت پیام‌هاست...")
    
    def stop_polling(self):
        """توقف ربات"""
        self.is_running = False
        if self.polling_thread:
            self.polling_thread.join(timeout=5)
        logger.info("🛑 ربات متوقف شد.")

# ایجاد نمونه ربات
bot = Six3yesBot()

@app.route('/')
def home():
    return "🤖 ربات Six3yes فعال است! /start را در روبیکا امتحان کنید."

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "bot": "running"})

@app.route('/start-bot')
def start_bot():
    """این endpoint ربات را راه‌اندازی می‌کند (مفید برای بیدار کردن از خواب)"""
    bot.start_polling()
    return jsonify({"message": "ربات راه‌اندازی شد"})

@app.route('/stop-bot')
def stop_bot():
    """این endpoint ربات را متوقف می‌کند"""
    bot.stop_polling()
    return jsonify({"message": "ربات متوقف شد"})

# ================== راه‌اندازی اصلی ==================
def start_bot_on_load():
    """این تابع وقتی برنامه بارگذاری می‌شود اجرا می‌شود"""
    logger.info("🔧 برنامه بارگذاری شد، در حال راه‌اندازی ربات...")
    time.sleep(2)  # کمی تاخیر برای اطمینان از بارگذاری کامل
    bot.start_polling()

# ثبت تابع برای اجرا هنگام بارگذاری
@app.before_first_request
def before_first_request():
    """این تابع قبل از اولین درخواست به برنامه اجرا می‌شود"""
    start_bot_on_load()

# همچنین هنگام شروع برنامه هم اجرا می‌شود
if __name__ == "__main__":
    start_bot_on_load()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # برای زمانی که با gunicorn اجرا می‌شود
    start_bot_on_load()
