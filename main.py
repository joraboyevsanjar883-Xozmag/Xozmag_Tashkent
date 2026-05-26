import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, KeyboardButton, WebAppInfo, ReplyKeyboardRemove, FSInputFile
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# TOKEN va ADMIN ID
TOKEN = "8624663091:AAEeuXAxCj85QeGIbAkLwsMgpTRYPhBpRMI"
ADMIN_ID = 1181202230  

PAYME_APP_LINK = "https://payme.uz/fallback/pay/64cb5d7b5b15be60bd5e8cc7"
WEB_APP_URL = "https://joraboyevsanjar883-xozmag.github.io/Xozmag_Tashkent/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_payment = State()

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🛍 Katalog (Do'kon)", web_app=WebAppInfo(url=WEB_APP_URL)))
    builder.add(KeyboardButton(text="🔄 Qayta boshlash"))
    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("👋 Assalomu alaykum! Katalogdan tanlang:", reply_markup=get_main_keyboard())

@dp.message(F.text == "🔄 Qayta boshlash")
async def restart_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔄 Bot qayta boshlandi.", reply_markup=get_main_keyboard())

@dp.message(F.web_app_data)
async def web_app_data_handler(message: Message, state: FSMContext):
    data = json.loads(message.web_app_data.data)
    await state.update_data(cart_items=data['items'], total_price=data['total'])
    await message.answer("👤 Ism-familiyangizni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.waiting_for_name)

@dp.message(OrderState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True))
    await message.answer("📞 Telefoningizni yuboring:", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True))
    await message.answer("📍 Manzilni kiriting yoki Lokatsiya yuboring:", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_address)

@dp.message(OrderState.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    address = f"📍 Lokatsiya: {message.location.latitude}, {message.location.longitude}" if message.location else message.text
    await state.update_data(address=address)
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="💵 Naqd pul"), KeyboardButton(text="💳 Elektron to'lov (Payme)"))
    builder.adjust(2)
    await message.answer("💳 To'lov usulini tanlang:", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_payment)

@dp.message(OrderState.waiting_for_payment)
async def process_payment(message: Message, state: FSMContext):
    await state.update_data(payment=message.text)
    order_data = await state.get_data()
    if message.text == "💳 Elektron to'lov (Payme)":
        inline_builder = InlineKeyboardBuilder()
        inline_builder.button(text="🔹 PAYME orqali to'lash", url=PAYME_APP_LINK)
        await message.answer(f"💰 Jami: {order_data['total_price']} so'm.\nTo'lang va chekni shu yerga yuboring!", reply_markup=inline_builder.as_markup())
    else:
        await message.answer("🎉 Buyurtmangiz qabul qilindi!", reply_markup=get_main_keyboard())
        await state.clear()

@dp.message(F.photo)
async def handle_photo_receipt(message: Message, state: FSMContext):
    await message.answer("✅ Chek qabul qilindi. Admin tekshirib aloqaga chiqadi.")
    order_data = await state.get_data()
    
    admin_text = (
        f"💳 <b>YANGI TO'LOV CHEKI!</b>\n\n"
        f"👤 Mijoz: {order_data.get('name', 'Noma\'lum')}\n"
        f"📞 Tel: {order_data.get('phone', 'Noma\'lum')}\n"
        f"💵 Jami: {order_data.get('total_price', 0)} so'm\n\n"
        f"🛒 <b>Tarkibi:</b>\n"
    )
    for item in order_data.get('cart_items', []):
        admin_text += f"▪️ {item['name']}: {item['price']} so'm\n"

    await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=admin_text, parse_mode="HTML")
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())