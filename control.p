from telethon import TelegramClient
import asyncio

api_id = 36197920
api_hash = '2ccde5b4efd9a1465286f2bbcfec4b05'
# Saytingiz orqali yaratilgan sessiya fayli yo'li
session_path = 'sessions/+99899xxxxxxx.session' 

async def main():
    client = TelegramClient(session_path, api_id, api_hash)
    await client.connect()

    # 1. Kontaktlar ro'yxatini olish
    dialogs = await client.get_dialogs(limit=10)
    print("--- Oxirgi chatlar ---")
    for dialog in dialogs:
        print(f"Ism: {dialog.name} | ID: {dialog.id}")

    # 2. Akkaunt nomidan xabar yuborish
    # await client.send_message('username_yoki_id', 'Salom, bu avtomatik xabar!')

    await client.disconnect()

asyncio.run(main())
