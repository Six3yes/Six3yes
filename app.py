import os
import requests
import time
import json
from datetime import datetime
from flask import Flask, jsonify
import threading
import logging

app = Flask(__name__)

# تنظیم لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن از متغیر محیطی
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
    "option1": """⏳ **زمان‌بندی دقیق ارائه ربات:**

🔴 **تاریخ نهایی ارائه: یک ماه دیگر** (حداکثر ۳۰ روز)

📌 **دلیل این زمان‌بندی:** تیم سازنده Six3yes در حال حاضر در شرایط خاصی قرار دارد و اعضای اصلی درگیر مسائل شخصی و تحصیلی هستند. با این حال، کیفیت ربات برای ما از سرعت مهم‌تر است.

✨ **تعهد ما:** در این یک ماه، ربات را با بیش از ۱۵ قابلیت اصلی و تست کامل ارائه خواهیم داد.""",

    "option2": """🤖 **ویژگی‌های تأیید شده ربات Six3yes:**

🛡️ **۱. مدیریت هوشمند گروه:**
   • سیستم ضد لینک و ضد اسپم پیشرفته
   • دسترسی‌های سطح‌بندی شده

🧠 **۲. هوش مصنوعی اختصاصی:**
   • اتصال به موتورهای AI پیشرفته
   • پاسخ‌های مطلوب، سرگرم‌کننده و آموزنده

🎮 **۳. مجموعه بازی‌های ساده و جذاب:**
   • بازی تاس (Dice)
   • حدس عدد
   • سنگ‌کاغذ‌قیچی""",

    "option3": """⚠️ **هشدار! محتوای زیر ممکن است ترسناک باشد!**

😱 **ارور کیست؟** فردی بسیار خطرناک و مرموز که ادعا می‌کند در حرفه "هکیر"ی (نه هکر، حتماً با "ر" بخوانید!) از همه بهتر است!

🎭 **حقیقت ماجرا:** در واقعیت، ارور معمولاً مشغول مسخره کردن دوستانش است و تخصص اصلی‌اش ایجاد باگ‌های عجیب در کدهاست!""",

    "option4": """👑 **مالک و سازنده اصلی:**

• **نام:** آرین
• **شماره تماس:** `+98 939 625 5842`
• **مسئولیت:** مدیر پروژه، تصمیم‌گیر نهایی، عاشق فناوری

🎯 **درباره مالک:** آرین فردی با انگیزه و پرتلاش است که این پروژه را با عشق و صرف زمان شخصی راه‌اندازی کرده."""
}

class Six3yesBot:
    def __init__(self):
        self.is_running = False
        logger.info("🤖 ربات Six3yes راه‌اندازی شد")
    
    def send_message(self, chat_id, text):
        try:
            payload = {"chat_id": chat_id, "text": text[:4000]}
            response = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ پیام ارسال شد به {chat_id}")
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
    
    def run_polling(self):
        if self.is_running:
            logger.warning("⚠️ ربات در حال اجراست!")
            return
        
        self.is_running = True
        logger.info("📡 شروع دریافت پیام‌ها...")
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
                                        logger.info(f"📩 پیام از {chat_id}: {text[:30]}...")
                                        reply = self.process_text(text)
                                        self.send_message(chat_id, reply)
                
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"⚠️ خطا در polling: {e}")
                time.sleep(5)
    
    def stop(self):
        self.is_running = False
        logger.info("🛑 ربات متوقف شد")

# ایجاد نمونه ربات
bot = Six3yesBot()

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Six3yes Bot</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f0f0; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #4a4a4a; }
            .status { color: green; font-weight: bold; }
            .bot-name { color: #3498db; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 ربات <span class="bot-name">Six3yes</span></h1>
            <p class="status">✅ فعال و آنلاین</p>
            <p>ربات در حال اجراست و پیام‌ها را پردازش می‌کند.</p>
            <p>برای استفاده، در روبیکا به ربات پیام دهید.</p>
            <hr>
            <p><small>ساخته شده با ❤️ توسط تیم Six3yes</small></p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "bot": "running"})

@app.route('/start-bot', methods=['POST'])
def start_bot_route():
    thread = threading.Thread(target=bot.run_polling, daemon=True)
    thread.start()
    return jsonify({"message": "ربات شروع به کار کرد"})

# شروع ربات در background
if __name__ == "__main__":
    # شروع ربات در یک thread جداگانه
    bot_thread = threading.Thread(target=bot.run_polling, daemon=True)
    bot_thread.start()
    
    # اجرای Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # برای زمانی که با gunicorn اجرا می‌شود
    bot_thread = threading.Thread(target=bot.run_polling, daemon=True)
    bot_thread.start()
