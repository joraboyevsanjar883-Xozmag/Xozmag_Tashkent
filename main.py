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

logging.basicConfig(level=logging.INFO)

TOKEN = "8624663091:AAEeuXAxCj85QeGIbAkLwsMgpTRYPhBpRMI"
WEB_APP_URL = "https://joraboyevsanjar883-xozmag.github.io/Xozmag_Tashkent/"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    # Reply keyboard orqali til tanlatamiz
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский"))
    builder.adjust(2)
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский"]))
async def process_lang(message: Message, state: FSMContext):
    lang_code = "rus" if message.text == "🇷🇺 Русский" else "uz"
    await state.update_data(lang=lang_code)
    
    # Inline Katalog tugmasi
    builder = InlineKeyboardBuilder()
    text = "🛍 Katalog" if lang_code == "uz" else "🛍 Каталог"
    builder.add(InlineKeyboardButton(text=text, web_app={"url": f"{WEB_APP_URL}?lang={lang_code}"}))
    
    # Eski klaviaturani butunlay o'chiramiz
    await message.answer("✅", reply_markup=ReplyKeyboardRemove()) 
    await message.answer("Katalogga o'tish:" if lang_code == "uz" else "Перейти в каталог:", reply_markup=builder.as_markup())

@dp.message(F.web_app_data)
async def web_data(message: Message, state: FSMContext):
    # WebApp dan ma'lumot qabul qilish
    data = json.loads(message.web_app_data.data)
    await state.update_data(price=data.get('total'))
    lang = (await state.get_data()).get('lang')
    
    txt = "👤 Ism-familiyangizni kiriting:" if lang == "uz" else "👤 Введите ваше имя:"
    await message.answer(txt, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.waiting_for_name)

@dp.message(OrderState.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    lang = (await state.get_data()).get('lang')
    
    builder = ReplyKeyboardBuilder()
    btn = "📱 Raqamni yuborish" if lang == "uz" else "📱 Отправить номер"
    builder.add(KeyboardButton(text=btn, request_contact=True))
    await message.answer("📞 Raqamingizni yuboring:" if lang == "uz" else "📞 Отправьте ваш номер:", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    lang = (await state.get_data()).get('lang')
    
    txt = "📍 Manzilingizni kiriting:" if lang == "uz" else "📍 Введите ваш адрес:"
    await message.answer(txt, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.waiting_for_address)

@dp.message(OrderState.waiting_for_address)
async def get_addr(message: Message, state: FSMContext):
    d = await state.get_data()
    txt = f"✅ Buyurtma qabul qilindi!\nNarxi: {d['price']} so'm" if d['lang'] == "uz" else f"✅ Заказ принят!\nИтого: {d['price']} сум"
    await message.answer(txt)
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())