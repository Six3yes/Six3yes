import os
import requests
import time
import json
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
        self.thread = None
        self.last_update_id = 0  # اینجا آخرین آپدیت را ذخیره می‌کنیم
        logger.info("🤖 ربات Six3yes راه‌اندازی شد.")
    
    def send_message(self, chat_id, text):
        """ارسال پیام به کاربر"""
        try:
            payload = {"chat_id": chat_id, "text": text[:4000]}
            response = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ پاسخ ارسال شد به {chat_id[:12]}...")
                return True
            else:
                logger.error(f"❌ خطا در ارسال پاسخ: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ خطا در ارسال: {e}")
            return False
    
    def process_text(self, text):
        """پردازش متن و انتخاب پاسخ مناسب"""
        text = text.strip().lower()
        
        if text in ["/start", "start", "شروع", "استارت"]:
            return RESPONSES["start"]
        elif text in ["1", "گزینه 1", "زمان‌بندی", "زمانبندی"]:
            return RESPONSES["option1"]
        elif text in ["2", "گزینه 2", "ویژگی", "ویژگی‌ها"]:
            return RESPONSES["option2"]
        elif text in ["3", "گزینه 3", "ارور", "ارور کیست"]:
            return RESPONSES["option3"]
        elif text in ["4", "گزینه 4", "مالک", "سازنده"]:
            return RESPONSES["option4"]
        else:
            return "🤖 لطفاً عدد ۱ تا ۴ را انتخاب کنید یا دستور /start را وارد نمایید."
    
    def polling_loop(self):
        """حلقه اصلی دریافت پیام‌ها از روبیکا"""
        logger.info("📡 شروع دریافت پیام‌ها از روبیکا...")
        
        while self.is_running:
            try:
                # ساختار درخواست بر اساس پاسخ موفق آزمایش
                payload = {"start_id": self.last_update_id}
                
                response = requests.post(
                    f"{BASE_URL}/getUpdates", 
                    json=payload, 
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "OK":
                        updates = data.get("data", {}).get("updates", [])
                        
                        for update in updates:
                            update_id = update.get("update_id")
                            
                            # فقط آپدیت‌های جدید را پردازش کن
                            if update_id and update_id > self.last_update_id:
                                self.last_update_id = update_id
                                
                                # فقط پیام‌های متنی جدید را پردازش کن
                                if update.get("type") == "NewMessage":
                                    new_message = update.get("new_message", {})
                                    text = new_message.get("text", "").strip()
                                    chat_id = update.get("chat_id")
                                    
                                    if text and chat_id:
                                        logger.info(f"📩 پیام جدید از {chat_id[:12]}...: {text[:30]}")
                                        reply = self.process_text(text)
                                        self.send_message(chat_id, reply)
                
                # کمی صبر کن تا سرور روبیکا تحت فشار نباشد
                time.sleep(3)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"🌐 خطای شبکه: {e}")
                time.sleep(10)
            except Exception as e:
                logger.error(f"⚠️ خطای غیرمنتظره: {e}")
                time.sleep(10)
    
    def start(self):
        """شروع کار ربات"""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self.polling_loop, daemon=True)
        self.thread.start()
        logger.info("🚀 ربات شروع به کار کرد و آماده دریافت پیام است.")
    
    def stop(self):
        """توقف ربات"""
        self.is_running = False
        logger.info("🛑 ربات متوقف شد.")

# ================== راه‌اندازی ربات ==================
bot = Six3yesBot()

# ربات بلافاصله پس از بارگذاری شروع به کار می‌کند
bot.start()

@app.route('/')
def home():
    return "🤖 ربات Six3yes فعال است! /start را در روبیکا امتحان کنید."

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "bot": "running", "last_update_id": bot.last_update_id})

@app.route('/start-bot')
def start_bot_route():
    """این endpoint برای راه‌اندازی مجدد ربات پس از خواب Render مفید است"""
    bot.start()
    return jsonify({"message": "ربات راه‌اندازی شد.", "last_update_id": bot.last_update_id})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
