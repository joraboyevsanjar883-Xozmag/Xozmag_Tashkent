import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

TOKEN = "8624663091:AAEj6YvRD5Bv9CfFauyADcC2jXKmaQS6M2w"
ADMIN_ID = "1181202230"
WEB_APP_URL = "https://joraboyevsanjar883-xozmag.github.io/Xozmag_Tashkent/"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="O'zbekcha"), KeyboardButton(text="Русский"))
    builder.adjust(2)
    await message.answer("Tilni tanlang:", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text.in_(["O'zbekcha", "Русский"]))
async def process_lang(message: Message, state: FSMContext):
    lang = "rus" if message.text == "Русский" else "uz"
    await state.update_data(lang=lang)
    builder = InlineKeyboardBuilder()
    btn_text = "🛍 Katalog" if lang == "uz" else "🛍 Каталог"
    builder.add(InlineKeyboardButton(text=btn_text, web_app={"url": WEB_APP_URL}))
    await message.answer("✅", reply_markup=ReplyKeyboardRemove())
    await message.answer("Katalogga o'tish:" if lang == "uz" else "Перейти в каталог:", reply_markup=builder.as_markup())

# ENG MUHIM QISM
@dp.message(F.web_app_data)
async def web_data(message: Message, state: FSMContext):
    try:
        data = json.loads(message.web_app_data.data)
        await state.update_data(items=data.get('items'), total=data.get('total'))
        lang = (await state.get_data()).get('lang', 'uz')
        
        txt = f"✅ Buyurtma qabul qilindi!\nMahsulotlar: {data.get('items')}\nJami: {data.get('total')} so'm\n\nIsmingizni kiriting:" if lang == "uz" else f"✅ Заказ принят!\nТовары: {data.get('items')}\nИтого: {data.get('total')} сум\n\nВведите ваше имя:"
        await message.answer(txt, reply_markup=ReplyKeyboardRemove())
        await state.set_state(OrderState.waiting_for_name)
    except Exception as e:
        print(f"Xatolik: {e}")

@dp.message(OrderState.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=ReplyKeyboardBuilder().add(KeyboardButton(text="📱 Raqam", request_contact=True)).as_markup(resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    await message.answer("Manzilingizni yozing:")
    await state.set_state(OrderState.waiting_for_address)

@dp.message(OrderState.waiting_for_address)
async def get_addr(message: Message, state: FSMContext):
    d = await state.get_data()
    await bot.send_message(ADMIN_ID, f"YANGI BUYURTMA!\nMijoz: {d['name']}\nTel: {d['phone']}\nManzil: {message.text}\nMahsulotlar: {d['items']}\nJami: {d['total']}")
    await message.answer("✅ Buyurtmangiz qabul qilindi!")
    await state.clear()

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))