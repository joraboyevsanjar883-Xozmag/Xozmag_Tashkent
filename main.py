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

# 🔗 PAYME TIZIMI
PAYME_APP_LINK = "https://payme.uz/fallback/pay/64cb5d7b5b15be60bd5e8cc7"

# 🌐 GITHUB WEB APP LINKINGIZ
WEB_APP_URL = "https://joraboyevsanjar883-xozmag.github.io/Xozmag_Tashkent/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_payment = State()

# 🛍 ASOSIY MENYU
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🛍 Katalog (Do'kon)", web_app=WebAppInfo(url=WEB_APP_URL)))
    builder.add(KeyboardButton(text="🔄 Qayta boshlash"))
    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Assalomu alaykum! <b>Xozmag Tashkent</b> do'koniga xush kelibsiz.\n\n"
        "🛒 Katalogni ko'rish va xarid qilish uchun pastdagi <b>🛍 Katalog (Do'kon)</b> tugmasini bosing.",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "🔄 Qayta boshlash")
async def restart_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔄 Bot qayta boshlandi.", reply_markup=get_main_keyboard())

# 📥 WEB APP OYNASIDAN BUYURTMA KELGANDA
@dp.message(F.web_app_data)
async def web_app_data_handler(message: Message, state: FSMContext):
    data = json.loads(message.web_app_data.data)
    # HTML dagi kalitlarga moslashtirdik
    await state.update_data(cart_items=data['items'], total_price=data['total'])
    
    await message.answer("👤 Buyurtmani rasmiylashtirish uchun Ism-familiyangizni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.waiting_for_name)

@dp.message(OrderState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True))
    await message.answer("📞 Telefon raqamingizni pastdagi tugma orqali yuboring:", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True))
    await message.answer("📍 Manzilni kiriting yoki pastdagi tugma orqali Lokatsiya yuboring:", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_address)

@dp.message(OrderState.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    if message.location:
        address = f"📍 Lokatsiya: {message.location.latitude}, {message.location.longitude}"
    else:
        address = message.text
    await state.update_data(address=address)
    
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="💵 Naqd pul"))
    builder.add(KeyboardButton(text="💳 Elektron to'lov (Payme)"))
    builder.adjust(2)
    
    await message.answer("💳 To'lov usulini tanlang:", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(OrderState.waiting_for_payment)

@dp.message(OrderState.waiting_for_payment)
async def process_payment(message: Message, state: FSMContext):
    payment_method = message.text
    await state.update_data(payment=payment_method)
    
    order_data = await state.get_data()
    
    admin_text = (
        f"🚨 <b>YANGI BUYURTMA KELDI!</b>\n\n"
        f"👤 <b>Mijoz:</b> {order_data['name']}\n"
        f"📞 <b>Tel:</b> {order_data['phone']}\n"
        f"📍 <b>Manzil:</b> {order_data['address']}\n"
        f"💳 <b>To'lov turi:</b> {payment_method}\n\n"
        f"🛒 <b>Tovarlar:</b>\n"
    )
    
    for item in order_data['cart_items']:
        admin_text += f"▪️ {item['name']} - {item['price']} so'm\n"
        
    admin_text += f"\n💵 <b>Jami summa: {order_data['total_price']} so'm</b>\n"
    
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Admin xabar xatosi: {e}")
        
    if payment_method == "💳 Elektron to'lov (Payme)":
        inline_builder = InlineKeyboardBuilder()
        inline_builder.button(text="🔹 PAYME orqali to'lash", url=PAYME_APP_LINK)
        await message.answer(
            f"💰 <b>Jami summa:</b> {order_data['total_price']} so'm\n\n"
            f"To'lovni amalga oshiring va chekni shu yerga tashlang!",
            parse_mode="HTML",
            reply_markup=inline_builder.as_markup()
        )
    else:
        await message.answer("🎉 Rahmat! Naqd pul orqali buyurtmangiz qabul qilindi. Tez orada aloqaga chiqamiz.", reply_markup=get_main_keyboard())
        
    await state.clear()

@dp.message(F.photo)
async def handle_photo_receipt(message: Message):
    await message.answer("✅ To'lov chekingiz qabul qilindi. Admin tekshirib, buyurtmani kuryerga beradi.")
    await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption="Mijoz to'lov chekini yubordi!")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())