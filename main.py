import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, KeyboardButton, WebAppInfo, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = "8624663091:AAEeuXAxCj85QeGIbAkLwsMgpTRYPhBpRMI"
ADMIN_ID = 1181202230
PAYME_APP_LINK = "https://payme.uz/fallback/pay/64cb5d7b5b15be60bd5e8cc7"
WEB_APP_URL = "https://joraboyevsanjar883-xozmag.github.io/Xozmag_Tashkent/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class OrderState(StatesGroup):
    waiting_for_lang = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_payment = State()

# Tilga qarab keyboard yasash funksiyasi
def get_main_keyboard(lang):
    builder = ReplyKeyboardBuilder()
    if lang == "🇺🇿 O'zbekcha":
        builder.add(KeyboardButton(text="🛍 Katalog (Do'kon)", web_app=WebAppInfo(url=WEB_APP_URL)))
        builder.add(KeyboardButton(text="🔄 Qayta boshlash"))
    else:
        builder.add(KeyboardButton(text="🛍 Каталог (Магазин)", web_app=WebAppInfo(url=WEB_APP_URL)))
        builder.add(KeyboardButton(text="🔄 Перезапустить"))
    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский"))
    builder.adjust(2)
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_lang)

@dp.message(OrderState.waiting_for_lang)
async def process_language(message: Message, state: FSMContext):
    lang = message.text
    await state.update_data(lang=lang)
    text = "Xush kelibsiz!" if lang == "🇺🇿 O'zbekcha" else "Добро пожаловать!"
    await message.answer(text, reply_markup=get_main_keyboard(lang))
    await state.set_state(None) # Holatni tozalaymiz

@dp.message(F.text.in_({"🔄 Qayta boshlash", "🔄 Перезапустить"}))
async def restart_handler(message: Message, state: FSMContext):
    await state.clear()
    await command_start_handler(message, state)

@dp.message(F.web_app_data)
async def web_app_data_handler(message: Message, state: FSMContext):
    data = json.loads(message.web_app_data.data)
    user_data = await state.get_data()
    lang = user_data.get('lang', "🇺🇿 O'zbekcha")
    
    await state.update_data(cart_items=data['items'], total_price=data['total'])
    
    txt = "👤 Ism-familiyangizni kiriting:" if lang == "🇺🇿 O'zbekcha" else "👤 Введите ваше имя:"
    await message.answer(txt, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.waiting_for_name)

# --- Qolgan barcha OrderState qismlariga ham xuddi shunday 'lang' tekshiruvini qo'shishingiz kerak ---
# Misol uchun:
@dp.message(OrderState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    user_data = await state.get_data()
    lang = user_data.get('lang', "🇺🇿 O'zbekcha")
    
    builder = ReplyKeyboardBuilder()
    txt_btn = "📱 Telefon raqamni yuborish" if lang == "🇺🇿 O'zbekcha" else "📱 Отправить номер телефона"
    builder.add(KeyboardButton(text=txt_btn, request_contact=True))
    
    txt_msg = "📞 Telefoningizni yuboring:" if lang == "🇺🇿 O'zbekcha" else "📞 Отправьте ваш номер телефона:"
    await message.answer(txt_msg, reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_phone)

# ... qolgan funksiyalarni ham xuddi shu mantiqda o'zgartirasiz ...

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())