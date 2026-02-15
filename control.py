from telethon import TelegramClient
import asyncio
import os

# API ma'lumotlaringiz
api_id = 36197920
api_hash = '2ccde5b4efd9a1465286f2bbcfec4b05'

async def manage_account():
    # Sessions papkasidagi birinchi mavjud sessiyani topish
    session_files = [f for f in os.listdir('sessions') if f.endswith('.session')]
    
    if not session_files:
        print("❌ Hech qanday sessiya fayli topilmadi!")
        return

    # Birinchi sessiya faylini tanlaymiz
    session_name = f"sessions/{session_files[0].replace('.session', '')}"
    print(f"🔄 Ulanyapti: {session_name}")

    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        print("❌ Sessiya muddati o'tgan yoki noto'g'ri.")
        return

    me = await client.get_me()
    print(f"\n✅ Akkauntga ulanildi: {me.first_name} (@{me.username})")

    # 1. Oxirgi 5 ta xabarni ko'rish
    print("\n📩 Oxirgi chatlaringiz:")
    async for dialog in client.iter_dialogs(limit=5):
        print(f"- {dialog.name} (ID: {dialog.id})")

    # 2. O'zingizga (Saved Messages) hisobot yuborish
    await client.send_message('me', '🛡️ Akkaunt xavfsizligi tekshirildi. Sessiya boshqaruvi ishlamoqda.')
    print("\n🚀 'Saved Messages'ga hisobot yuborildi.")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(manage_account())
