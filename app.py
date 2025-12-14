import os
import requests
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# تنظیم لاگ‌گیری
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== تنظیمات ==================
TOKEN = os.environ.get("RUBIKA_TOKEN", "FBICI0TARGDLXTXZUBLYODAGLEPQXKRDDQPJWZDIHSVKSEDBOKBVVPCNWPUTILSF")
BASE_URL = f"https://botapi.rubika.ir/v3/{TOKEN}"

# ================== پاسخ‌های کامل ==================
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

# ================== تابع ارسال پیام ==================
def send_message(chat_id, text, reply_to=None):
    """ارسال پیام با لاگ‌گیری و مدیریت خطا"""
    try:
        payload = {
            "chat_id": chat_id,
            "text": text[:4000]
        }
        
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        
        logger.info(f"📤 ارسال پیام به {chat_id[:12]}...: {text[:30]}...")
        
        response = requests.post(
            f"{BASE_URL}/sendMessage",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ پیام ارسال شد")
            return True
        else:
            logger.error(f"❌ خطا در ارسال: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ خطای شبکه در ارسال: {e}")
        return False

# ================== پردازش پیام ==================
def process_message(text, chat_id, message_id):
    """پردازش متن پیام و انتخاب پاسخ"""
    text = text.strip().lower()
    
    if text in ["/start", "start", "شروع", "استارت"]:
        return RESPONSES["start"]
    elif text in ["1", "۱", "گزینه 1", "زمان‌بندی"]:
        return RESPONSES["option1"]
    elif text in ["2", "۲", "گزینه 2", "ویژگی"]:
        return RESPONSES["option2"]
    elif text in ["3", "۳", "گزینه 3", "ارور"]:
        return RESPONSES["option3"]
    elif text in ["4", "۴", "گزینه 4", "مالک"]:
        return RESPONSES["option4"]
    else:
        return "🤖 لطفاً عدد ۱ تا ۴ را انتخاب کنید یا /start را بفرستید."

# ================== Webhook اصلی ==================
@app.route("/webhook", methods=["POST"])
def webhook():
    """دریافت پیام‌ها از روبیکا"""
    try:
        data = request.json
        logger.info(f"📥 دریافت Webhook: {json.dumps(data)[:200]}...")
        
        if not data:
            logger.warning("⚠️ داده خالی دریافت شد")
            return jsonify({"ok": False, "error": "No data"}), 400
        
        # بررسی ساختار داده‌های روبیکا (با توجه به لاگ‌های قبلی)
        if "data" in data and "updates" in data["data"]:
            # ساختار Polling (همان‌طور که در لاگ‌ها دیدیم)
            updates = data["data"]["updates"]
            
            for update in updates:
                if update.get("type") == "NewMessage":
                    new_message = update.get("new_message", {})
                    text = new_message.get("text", "").strip()
                    chat_id = update.get("chat_id")
                    message_id = new_message.get("message_id")
                    
                    if text and chat_id:
                        logger.info(f"📩 پیام جدید: '{text[:20]}...' از {chat_id[:12]}...")
                        response_text = process_message(text, chat_id, message_id)
                        send_message(chat_id, response_text, message_id)
        
        elif "update" in data:
            # ساختار Webhook (مطابق کد شما)
            update = data["update"]
            new_message = update.get("message", {})
            
            text = new_message.get("text", "").strip()
            chat_id = new_message.get("chat_id")
            message_id = new_message.get("message_id")
            
            if text and chat_id:
                logger.info(f"📩 پیام Webhook: '{text[:20]}...' از {chat_id[:12]}...")
                response_text = process_message(text, chat_id, message_id)
                send_message(chat_id, response_text, message_id)
        else:
            logger.warning(f"⚠️ ساختار ناشناخته: {data}")
        
        return jsonify({"ok": True, "message": "Processed"})
        
    except Exception as e:
        logger.error(f"❌ خطا در پردازش Webhook: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

# ================== صفحه‌های کمکی ==================
@app.route("/")
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
            .endpoint { background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 ربات <span class="bot-name">Six3yes</span></h1>
            <p class="status">✅ فعال و آنلاین</p>
            <p>ربات با استفاده از Webhook فعال است.</p>
            
            <div class="endpoint">
                <strong>Webhook Endpoint:</strong><br>
                <code>POST https://six3yes.onrender.com/webhook</code>
            </div>
            
            <div class="endpoint">
                <strong>تست سلامت:</strong><br>
                <a href="/health">/health</a>
            </div>
            
            <p>برای تست ربات، در روبیکا به آن پیام دهید.</p>
            <hr>
            <p><small>ساخته شده با ❤️ توسط تیم Six3yes</small></p>
        </div>
    </body>
    </html>
    """

@app.route("/health")
def health():
    """بررسی سلامت سرویس"""
    return jsonify({
        "status": "healthy",
        "service": "Six3yes Webhook Bot",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "webhook": "/webhook",
            "home": "/",
            "health": "/health"
        }
    })

@app.route("/test-send", methods=["POST"])
def test_send():
    """تست ارسال پیام (برای آزمایش دستی)"""
    try:
        chat_id = "b0IgJ3V0Nve0d0a32074044f4d118c86"  # از لاگ‌های قبلی
        text = "✅ تست Webhook از سرور Render"
        
        result = send_message(chat_id, text)
        
        return jsonify({
            "success": result,
            "message": "پیام تست ارسال شد",
            "chat_id": chat_id[:12] + "..."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================== اجرای برنامه ==================
if __name__ == "__main__":
    logger.info("🚀 راه‌اندازی ربات Six3yes با Webhook...")
    
    # تست اولیه اتصال
    try:
        logger.info("🔍 تست اتصال به API روبیکا...")
        test_resp = requests.get(f"{BASE_URL}/getMe", timeout=10)
        logger.info(f"✅ تست اتصال: کد {test_resp.status_code}")
    except Exception as e:
        logger.error(f"❌ خطا در تست اتصال: {e}")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
