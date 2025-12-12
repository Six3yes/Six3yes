import os
import requests
import time
import json
from datetime import datetime
from flask import Flask, jsonify
import threading
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== تنظیمات ==================
TOKEN = os.environ.get("RUBIKA_TOKEN", "FBICI0TARGDLXTXZUBLYODAGLEPQXKRDDQPJWZDIHSVKSEDBOKBVVPCNWPUTILSF")
BASE_URL = f"https://botapi.rubika.ir/v3/{TOKEN}"

RESPONSES = {
    "start": """✨ **سلام! به ربات Six3yes خوش آمدی!** ✨\n👇عدد بفرست:\n1️⃣ زمان‌بندی\n2️⃣ ویژگی‌ها\n3️⃣ ارور کیست؟\n4️⃣ مالک""",
    "option1": """⏳ **زمان‌بندی:**\n🔴 حداکثر ۳۰ روز آینده.""",
    "option2": """🤖 **ویژگی‌ها:**\n🛡️ مدیریت گروه\n🧠 هوش مصنوعی\n🎮 بازی‌ها""",
    "option3": """⚠️ **ارور:** یک 'هکیر' خیالی!""",
    "option4": """👑 **مالک:**\n• آرین\n• +98 939 625 5842"""
}

# ================== کلاس ربات ==================
class Six3yesBot:
    def __init__(self):
        self.is_running = False
        self.thread = None
        logger.info("🤖 نمونه ربات ساخته شد.")

    def send_message(self, chat_id, text):
        try:
            payload = {"chat_id": chat_id, "text": text[:4000]}
            r = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
            if r.status_code == 200:
                logger.info(f"✅ ارسال به {chat_id[:8]}...")
                return True
            else:
                logger.error(f"❌ خطای {r.status_code} در ارسال")
                return False
        except Exception as e:
            logger.error(f"❌ خطا در ارسال: {e}")
            return False

    def process_text(self, text):
        text = text.strip().lower()
        if text in ["/start", "start", "شروع"]:
            return RESPONSES["start"]
        elif text in ["1", "زمانبندی"]:
            return RESPONSES["option1"]
        elif text in ["2", "ویژگی"]:
            return RESPONSES["option2"]
        elif text in ["3", "ارور"]:
            return RESPONSES["option3"]
        elif text in ["4", "مالک"]:
            return RESPONSES["option4"]
        else:
            return "لطفاً عدد ۱ تا ۴ یا /start را بفرستید."

    def polling_loop(self):
        logger.info("📡 حلقه دریافت پیام‌ها شروع شد.")
        last_update_id = 0
        while self.is_running:
            try:
                payload = {"start_id": last_update_id} if last_update_id > 0 else {}
                r = requests.post(f"{BASE_URL}/getUpdates", json=payload, timeout=30)
                if r.status_code == 200:
                    data = r.json()
                    if data.get("status") == "OK":
                        for update in data.get("data", {}).get("updates", []):
                            update_id = update.get("update_id", 0)
                            if update_id > last_update_id:
                                last_update_id = update_id
                                if update.get("type") == "NewMessage":
                                    msg = update.get("new_message", {})
                                    text = msg.get("text", "").strip()
                                    chat_id = update.get("chat_id")
                                    if text and chat_id:
                                        logger.info(f"📩 پیام از {chat_id[:8]}...: {text[:20]}")
                                        reply = self.process_text(text)
                                        self.send_message(chat_id, reply)
                time.sleep(2)
            except requests.exceptions.RequestException as e:
                logger.error(f"🌐 خطای شبکه: {e}")
                time.sleep(5)
            except Exception as e:
                logger.error(f"⚠️ خطای ناشناخته: {e}")
                time.sleep(5)
        logger.info("🛑 حلقه دریافت متوقف شد.")

    def start(self):
        if self.is_running:
            logger.warning("⚠️ ربات از قبل در حال اجراست.")
            return
        self.is_running = True
        self.thread = threading.Thread(target=self.polling_loop, daemon=True)
        self.thread.start()
        logger.info("🚀 ربات شروع به کار کرد.")

# ================== راه‌اندازی Flask و ربات ==================
bot = Six3yesBot()

# *** تغییر اصلی اینجاست: ربات بلافاصله پس از بارگذاری ماژول شروع می‌شود ***
logger.info("🔧 بارگذاری برنامه...")
time.sleep(3)  # تاخیر کوتاه برای اطمینان از بارگذاری کامل
bot.start()
logger.info("✅ راه‌اندازی اولیه کامل شد.")

@app.route('/')
def home():
    return "ربات فعال است. /start را در روبیکا بفرستید."

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "bot": "running"})

@app.route('/start-bot')
def start_bot():
    """اگر ربات به هر دلیلی متوقف شد، این endpoint آن را دوباره راه می‌اندازد."""
    bot.start()
    return jsonify({"message": "دستور شروع ارسال شد."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
