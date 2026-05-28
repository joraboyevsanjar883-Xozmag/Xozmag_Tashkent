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
WEB_APP_URL = "https://joraboyevsanjar883-xozmag.github.io/Xozmag_Tashkent/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class OrderState(StatesGroup):
    waiting_for_lang = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_payment = State()

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
    lang_code = "rus" if lang == "🇷🇺 Русский" else "uz"
    await state.update_data(lang=lang, lang_code=lang_code)
    
    # URL ga tilni qo'shib yuboramiz
    url = f"{WEB_APP_URL}?lang={lang_code}"
    
    builder = ReplyKeyboardBuilder()
    btn_text = "🛍 Katalog (Do'kon)" if lang == "🇺🇿 O'zbekcha" else "🛍 Каталог (Магазин)"
    restart_text = "🔄 Qayta boshlash" if lang == "🇺🇿 O'zbekcha" else "🔄 Перезапустить"
    
    builder.add(KeyboardButton(text=btn_text, web_app=WebAppInfo(url=url)))
    builder.add(KeyboardButton(text=restart_text))
    builder.adjust(1)
    
    await message.answer("✅ Til tanlandi. Katalogga o'ting:", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(None)

@dp.message(F.text.in_({"🔄 Qayta boshlash", "🔄 Перезапустить"}))
async def restart_handler(message: Message, state: FSMContext):
    await state.clear()
    await command_start_handler(message, state)

@dp.message(F.web_app_data)
async def web_app_data_handler(message: Message, state: FSMContext):
    data = json.loads(message.web_app_data.data)
    await state.update_data(cart_items=data['items'], total_price=data['total'])
    
    lang = (await state.get_data()).get('lang')
    txt = "👤 Ism-familiyangizni kiriting:" if lang == "🇺🇿 O'zbekcha" else "👤 Введите ваше имя:"
    await message.answer(txt, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.waiting_for_name)

@dp.message(OrderState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    lang = (await state.get_data()).get('lang')
    
    builder = ReplyKeyboardBuilder()
    txt = "📱 Telefon raqamni yuborish" if lang == "🇺🇿 O'zbekcha" else "📱 Отправить номер"
    builder.add(KeyboardButton(text=txt, request_contact=True))
    await message.answer("📞 Telefoningizni yuboring:", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_phone)

# ... qolgan bosqichlarni ham xuddi shunday davom ettirasiz ...

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())