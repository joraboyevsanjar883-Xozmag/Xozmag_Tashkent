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

# O'zingizning TOKEN va ADMIN_ID ni kiriting
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
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text.in_(["O'zbekcha", "Русский"]))
async def process_lang(message: Message, state: FSMContext):
    lang = "rus" if message.text == "Русский" else "uz"
    await state.update_data(lang=lang)
    
    builder = InlineKeyboardBuilder()
    text = "🛍 Katalog" if lang == "uz" else "🛍 Каталог"
    builder.add(InlineKeyboardButton(text=text, web_app={"url": WEB_APP_URL}))
    
    await message.answer("✅", reply_markup=ReplyKeyboardRemove())
    await message.answer("Katalogga o'tish:" if lang == "uz" else "Перейти в каталог:", reply_markup=builder.as_markup())

# WEB APP DAN KELGAN MA'LUMOTNI QABUL QILISH
@dp.message(F.web_app_data)
async def web_app_handler(message: Message, state: FSMContext):
    data = json.loads(message.web_app_data.data)
    items = data.get("items")
    total = data.get("total")
    
    await state.update_data(items=items, total=total)
    
    d = await state.get_data()
    lang = d.get('lang', 'uz')
    
    text = f"✅ Buyurtmangiz qabul qilindi!\n\n🛍 Mahsulotlar: {items}\n💰 Jami: {total} so'm\n\n👤 Iltimos, ism-familiyangizni kiriting:" if lang == 'uz' else f"✅ Ваш заказ принят!\n\n🛍 Товары: {items}\n💰 Итого: {total} сум\n\n👤 Пожалуйста, введите ваше имя:"
    
    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.waiting_for_name)

@dp.message(OrderState.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    lang = (await state.get_data()).get('lang', 'uz')
    builder = ReplyKeyboardBuilder()
    btn = "📱 Raqamni yuborish" if lang == "uz" else "📱 Отправить номер"
    builder.add(KeyboardButton(text=btn, request_contact=True))
    
    txt = "📞 Telefon raqamingizni yuboring:" if lang == "uz" else "📞 Отправьте ваш номер:"
    await message.answer(txt, reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    lang = (await state.get_data()).get('lang', 'uz')
    
    txt = "📍 Manzilingizni kiriting:" if lang == "uz" else "📍 Введите ваш адрес:"
    await message.answer(txt, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.waiting_for_address)

@dp.message(OrderState.waiting_for_address)
async def get_addr(message: Message, state: FSMContext):
    d = await state.get_data()
    lang = d.get('lang', 'uz')
    
    admin_txt = (f"📦 YANGI BUYURTMA!\n\n"
                 f"👤 Mijoz: {d['name']}\n📞 Tel: {d['phone']}\n📍 Manzil: {message.text}\n\n"
                 f"🛒 Tovarlar: {d['items']}\n💰 Jami: {d['total']} so'm")
    
    await bot.send_message(ADMIN_ID, admin_txt)
    txt = "✅ Buyurtmangiz qabul qilindi!" if lang == "uz" else "✅ Ваш заказ принят!"
    await message.answer(txt)
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())