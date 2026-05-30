import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# 1. SOZLAMALAR
TOKEN = "8624663091:AAEj6YvRD5Bv9CfFauyADcC2jXKmaQS6M2w"
ADMIN_ID = 1181202230  # SHU YERGA ID RAQAMINGIZNI YOZING
WEB_APP_URL = "https://joraboyevsanjar883-xozmag.github.io/Xozmag_Tashkent/"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# 2. HOLATLAR (STATES)
class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()

# 3. START KOMANDASI
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="O'zbekcha"), KeyboardButton(text="Русский"))
    builder.adjust(2)
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=builder.as_markup(resize_keyboard=True))

# 4. TIL TANLASH
@dp.message(F.text.in_(["O'zbekcha", "Русский"]))
async def process_lang(message: Message, state: FSMContext):
    lang = "rus" if message.text == "Русский" else "uz"
    await state.update_data(lang=lang)
    
    builder = InlineKeyboardBuilder()
    text = "🛍 Katalog" if lang == "uz" else "🛍 Каталог"
    builder.add(InlineKeyboardButton(text=text, web_app={"url": WEB_APP_URL}))
    
    await message.answer("✅", reply_markup=ReplyKeyboardRemove())
    await message.answer("Katalogga o'tish:", reply_markup=builder.as_markup())

# 5. WEBAPP MA'LUMOTINI OLISH
@dp.message(F.web_app_data)
async def web_data(message: Message, state: FSMContext):
    data = json.loads(message.web_app_data.data)
    await state.update_data(items=data.get('items'), total=data.get('total'))
    
    lang = (await state.get_data()).get('lang')
    txt = "👤 Ism-familiyangizni kiriting:" if lang == "uz" else "👤 Введите ваше имя:"
    await message.answer(txt, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.waiting_for_name)

# 6. ISMNI OLISH
@dp.message(OrderState.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    lang = (await state.get_data()).get('lang')
    builder = ReplyKeyboardBuilder()
    btn = "📱 Raqamni yuborish" if lang == "uz" else "📱 Отправить номер"
    builder.add(KeyboardButton(text=btn, request_contact=True))
    await message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_phone)

# 7. TELEFONNI OLISH
@dp.message(OrderState.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    lang = (await state.get_data()).get('lang')
    txt = "📍 Manzilingizni kiriting:" if lang == "uz" else "📍 Введите ваш адрес:"
    await message.answer(txt, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.waiting_for_address)

# 8. MANZILNI OLISH VA BUYURTMANI YUBORISH
@dp.message(OrderState.waiting_for_address)
async def get_addr(message: Message, state: FSMContext):
    d = await state.get_data()
    admin_txt = (f"📦 YANGI BUYURTMA!\n\n"
                 f"👤 Mijoz: {d['name']}\n"
                 f"📞 Tel: {d['phone']}\n"
                 f"📍 Manzil: {message.text}\n\n"
                 f"🛒 Tovarlar: {d['items']}\n"
                 f"💰 Jami: {d['total']} so'm")
    
    await bot.send_message(ADMIN_ID, admin_txt)
    await message.answer("✅ Buyurtmangiz qabul qilindi! Tez orada aloqaga chiqamiz.")
    await state.clear()

# 9. BOTNI ISHGA TUSHIRISH
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())