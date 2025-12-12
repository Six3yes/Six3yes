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

TOKEN = os.environ.get("RUBIKA_TOKEN", "FBICI0TARGDLXTXZUBLYODAGLEPQXKRDDQPJWZDIHSVKSEDBOKBVVPCNWPUTILSF")
BASE_URL = f"https://botapi.rubika.ir/v3/{TOKEN}"

# ================== تست اولیه API ==================
def test_rubika_api():
    """تست مستقیم اتصال به API روبیکا"""
    logger.info("🔍 در حال تست اتصال به API روبیکا...")
    try:
        # تست 1: متد GET به آدرس getMe
        url = f"{BASE_URL}/getMe"
        logger.info(f"درحال ارسال درخواست GET به: {url}")
        response = requests.get(url, timeout=15)
        logger.info(f"وضعیت: {response.status_code}")
        logger.info(f"محتوا (خام): {response.text}")
        
        # تست 2: متد POST با بدنه خالی به آدرس getUpdates (شبیه به کد اصلی)
        url = f"{BASE_URL}/getUpdates"
        logger.info(f"درحال ارسال درخواست POST به: {url}")
        response = requests.post(url, json={}, timeout=15)
        logger.info(f"وضعیت: {response.status_code}")
        logger.info(f"محتوا (خام): {response.text}")
        
        # تست 3: متد POST با پارامتر start_id
        response = requests.post(url, json={"start_id": 0}, timeout=15)
        logger.info(f"وضعیت با start_id=0: {response.status_code}")
        logger.info(f"محتوا: {response.text[:200]}...")
        
    except Exception as e:
        logger.error(f"❌ خطا در تست API: {e}")

# اجرای تست بلافاصله پس از بارگذاری
test_rubika_api()

# ================== ربات ساده‌شده ==================
RESPONSES = {
    "start": "سلام! ربات در حال آزمایش است. تست اولیه انجام شد.",
    "1": "گزینه 1",
    "2": "گزینه 2"
}

class SimpleBot:
    def __init__(self):
        self.is_running = True
        logger.info("🤖 ربات ساده راه‌اندازی شد")
        # شروع دریافت پیام در یک ترد جدا
        self.thread = threading.Thread(target=self.poll, daemon=True)
        self.thread.start()
    
    def poll(self):
        """حلقه ساده دریافت پیام"""
        logger.info("📡 شروع حلقه دریافت پیام...")
        last_id = 0
        
        while self.is_running:
            try:
                # لاگ هر چرخه
                logger.info(f"🔁 چک برای پیام جدید (last_id={last_id})...")
                
                # درخواست به API - چندین حالت را امتحان می‌کنیم
                payload = {"start_id": last_id}
                response = requests.post(
                    f"{BASE_URL}/getUpdates", 
                    json=payload, 
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.text
                    logger.info(f"📥 پاسخ دریافت شد: {data[:100]}...")
                    
                    # سعی می‌کنیم JSON را پارس کنیم
                    try:
                        json_data = response.json()
                        logger.info(f"📊 JSON پارس شد: نوع={type(json_data)}")
                        
                        # اینجا باید منطق پردازش پیام‌ها را اضافه کنیم
                        # فعلاً فقط لاگ می‌کنیم
                        if isinstance(json_data, dict):
                            if json_data.get("status") == "OK":
                                updates = json_data.get("data", {}).get("updates", [])
                                logger.info(f"🔢 تعداد آپدیت‌ها: {len(updates)}")
                                
                                for update in updates:
                                    update_id = update.get("update_id")
                                    if update_id and update_id > last_id:
                                        last_id = update_id
                                        logger.info(f"🆕 آپدیت جدید: ID={update_id}")
                            else:
                                logger.warning(f"⚠️ وضعیت غیر OK: {json_data.get('status')}")
                        else:
                            logger.warning(f"⚠️ ساختار JSON غیرمنتظره: {json_data}")
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ خطا در پارس JSON: {e}. متن پاسخ: {data[:200]}")
                else:
                    logger.error(f"❌ خطای HTTP: {response.status_code}")
                
                # انتظار بین چرخه‌ها
                time.sleep(5)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"🌐 خطای شبکه: {e}")
                time.sleep(10)
            except Exception as e:
                logger.error(f"⚠️ خطای ناشناخته: {e}")
                time.sleep(10)

# ایجاد ربات
bot = SimpleBot()

@app.route('/')
def home():
    return "ربات در حال آزمایش API. لاگ‌ها را در Render بررسی کنید."

@app.route('/health')
def health():
    return jsonify({"status": "testing", "api": "rubika"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
