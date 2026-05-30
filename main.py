import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

# O'z tokeningizni yozing
TOKEN = "8624663091:AAEj6YvRD5Bv9CfFauyADcC2jXKmaQS6M2w"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(F.web_app_data)
async def web_app_qabul(message: Message):
    # Ma'lumotni JSON dan o'qiymiz
    data = json.loads(message.web_app_data.data)
    
    # Mijozga javob yuboramiz
    await message.answer(f"✅ Buyurtma qabul qilindi!\n\nMahsulot: {data['mahsulot']}\nNarxi: {data['narx']} so'm")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())