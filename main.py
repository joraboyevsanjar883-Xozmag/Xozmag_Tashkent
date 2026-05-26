import json
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

# Tokeningizni shu yerga qo'ying
API_TOKEN = '8624663091:AAEeuXAxCj85QeGIbAkLwsMgpTRYPhBpRMI'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    url = "https://joraboyevsanjar883-xozmag.github.io/Xozmag_Tashkent/"
    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Katalog", web_app=WebAppInfo(url=url))]
    ])
    await message.answer("Xush kelibsiz! Katalogdan tanlang:", reply_markup=builder)

@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        total = data.get('total', 0)
        items = ", ".join([i.get('name', '') for i in data.get('items', [])])
        await message.answer(f"✅ Yangi buyurtma!\nMahsulotlar: {items}\nJami: {total} so'm")
    except Exception as e:
        await message.answer(f"Xatolik: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())