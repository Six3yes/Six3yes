import os
import requests
import time
import logging
from flask import Flask, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)  # تغییر به DEBUG برای جزئیات بیشتر
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("RUBIKA_TOKEN", "FBICI0TARGDLXTXZUBLYODAGLEPQXKRDDQPJWZDIHSVKSEDBOKBVVPCNWPUTILSF")
BASE_URL = f"https://botapi.rubika.ir/v3/{TOKEN}"

# ذخیره آخرین آپدیت
last_update_id = 0

def check_for_updates():
    """تابعی ساده برای چک کردن پیام‌های جدید"""
    global last_update_id
    logger.info(f"🔍 چک برای پیام‌های جدید با start_id={last_update_id}")
    
    try:
        payload = {"start_id": last_update_id}
        logger.debug(f"ارسال درخواست به: {BASE_URL}/getUpdates با داده: {payload}")
        
        response = requests.post(f"{BASE_URL}/getUpdates", json=payload, timeout=30)
        logger.debug(f"وضعیت پاسخ: {response.status_code}")
        logger.debug(f"متن پاسخ: {response.text[:500]}")  # ۵۰۰ کاراکتر اول
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK":
                updates = data.get("data", {}).get("updates", [])
                logger.info(f"✅ تعداد آپدیت‌های دریافتی: {len(updates)}")
                
                for update in updates:
                    update_id = update.get("update_id")
                    if update_id and update_id > last_update_id:
                        last_update_id = update_id
                        logger.info(f"🆕 آپدیت جدید با ID: {update_id}")
                        
                        if update.get("type") == "NewMessage":
                            msg = update.get("new_message", {})
                            text = msg.get("text", "")
                            chat_id = update.get("chat_id")
                            logger.info(f"📩 پیام متنی از {chat_id}: {text[:50]}")
                            return True  # پیام جدید پیدا شد
        else:
            logger.error(f"❌ خطای HTTP از روبیکا: {response.status_code}")
            
    except requests.exceptions.Timeout:
        logger.error("⏰ زمان اتصال به روبیکا تمام شد")
    except requests.exceptions.ConnectionError:
        logger.error("🌐 خطای اتصال به روبیکا")
    except Exception as e:
        logger.error(f"⚠️ خطای غیرمنتظره: {e}")
    
    return False  # پیام جدیدی پیدا نشد

@app.route('/')
def home():
    return "ربات در حال آزمایش. برای تست به /test-updates بروید."

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "bot": "running", 
        "last_update_id": last_update_id,
        "timestamp": time.time()
    })

@app.route('/test-updates')
def test_updates():
    """این مسیر را به صورت دستی برای تست فراخوانی کنید"""
    logger.info("--- شروع تست دستی دریافت پیام ---")
    has_update = check_for_updates()
    logger.info("--- پایان تست دستی دریافت پیام ---")
    
    if has_update:
        return jsonify({"message": "پیام جدید پیدا شد!", "last_update_id": last_update_id})
    else:
        return jsonify({"message": "پیام جدیدی یافت نشد.", "last_update_id": last_update_id})

@app.route('/send-test')
def send_test():
    """تست ارسال پیام"""
    try:
        # ارسال پیام به خودتان (شناسه چت را باید داشته باشید)
        test_chat_id = "b0IgJ3V0Nve0d0a32074044f4d118c86"  # از لاگ‌های قبلی
        payload = {"chat_id": test_chat_id, "text": "✅ تست از سرور رندر"}
        response = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
        
        return jsonify({
            "status": response.status_code,
            "response": response.text[:200]
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    logger.info("🚀 برنامه Flask راه‌اندازی شد")
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
