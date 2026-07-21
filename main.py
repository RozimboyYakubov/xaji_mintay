import logging
import asyncio
import html
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, URLInputFile

# 🤖 Bot tokeni va adminlar IDs ro'yxati (2 ta ID shu yerda)
API_TOKEN = '8859865253:AAE8pOhInSp7XHfcpHAmsRE53bi8M7JW0oI'  # O'zingizning bot tokeningizni kiriting
ADMIN_IDS = [5825744781, 8355014682]      # 👈 Shu yerga 1- va 2-admin ID larini yozing!

# 🏷 Mahsulotlar narxlari va qisqa kodlari
PRODUCTS = {
    "mintay": {"name": "🐟 Mintay", "price": 70000, "unit": "kg", "photo": "https://avatars.mds.yandex.net/get-altay/19593321/2a0000019c6c04333348f04925eb67be7feb/L_height"},
    "kfc": {"name": "🍗 KFC", "price": 80000, "unit": "kg", "photo": "https://avatars.mds.yandex.net/get-eda/3593277/d966a509c0eb54225ae5ff8b3432baae/M_height"},
    "shashlik": {"name": "🍢 Shashlik", "price": 13000, "unit": "dona", "photo": "https://uzbekistan.travel/storage/app/media/Yuliya/Shashlik/cropped-images/gizhduanskiy-shashlyk-62-0-0-0-0-1603857586.jpg"},
    "somsa": {"name": "🌙 Somsa", "price": 15000, "unit": "dona", "photo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSBZWt9G6q9eobEX3a2YNJSQyJfth6ko0-faLeEQNbD-ZkT2Ez-bJd8L9RC&s=10"},
    "sous": {"name": "🥫 Sous", "price": 10000, "unit": "dona", "photo": "https://img.magnific.com/premium-photo/chili-sauce-peppers-isolated-white_392895-696164.jpg?semt=ais_hybrid&w=740&q=80"},
    "cola": {"name": "🥤 Cola", "price": 17000, "unit": "dona", "photo": "https://i0.wp.com/carlsgrill.com/wp-content/uploads/2024/04/cocacola1.5.png?fit=500%2C500&ssl=1"},
    "fanta": {"name": "🥤 Fanta", "price": 17000, "unit": "dona", "photo": "https://images.uzum.uz/ce8a878v1htd23airm6g/original.jpg"},
    "pepsi": {"name": "🥤 Pepsi", "price": 17000, "unit": "dona", "photo": "https://restorecms.blob.core.windows.net/erd/products/images/0/500x500x75/4060800001702.jpg"},
    "flesh": {"name": "⚡ Flesh", "price": 12000, "unit": "dona", "photo": "https://dostavo4ka.uz/upload-file/2021/05/05/493/c07a1652-3982-44aa-8eeb-37cc0820484c.jpg"},
    "adrenalin": {"name": "⚡ Adrenalin", "price": 15000, "unit": "dona", "photo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ2PfJaePvEZzH4Pamihz3LlxW2xg9mvJ1-vZojG_nBRnKjTwJUugYejSXN&s=10"},
    "gorilla": {"name": "⚡ Gorilla", "price": 15000, "unit": "dona", "photo": "https://amwine.ru/upload/resize_cache/iblock/c2a/620_620_1/nv4cyo39tqvu46olei2zf86xr1u5f7yi.png"}
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class OrderState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_address = State()

def get_key_by_name(name):
    for key, data in PRODUCTS.items():
        if data["name"] == name:
            return key
    return None

# 🗂 Menyular
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🐟 Mintay"), KeyboardButton(text="🍗 KFC")],
        [KeyboardButton(text="🍢 Shashlik"), KeyboardButton(text="🌙 Somsa")],
        [KeyboardButton(text="🥤 Ichimliklar va Souslar")],
        [KeyboardButton(text="🛒 Savatni ko'rish / Rasmiylashtirish")]
    ],
    resize_keyboard=True
)

drinks_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🥫 Sous"), KeyboardButton(text="🥤 Cola"), KeyboardButton(text="🥤 Fanta")],
        [KeyboardButton(text="🥤 Pepsi"), KeyboardButton(text="⚡ Flesh"), KeyboardButton(text="⚡ Adrenalin")],
        [KeyboardButton(text="⚡ Gorilla"), KeyboardButton(text="⬅️ Orqaga")]
    ],
    resize_keyboard=True
)

def get_product_keyboard(p_key, amount=1):
    p_data = PRODUCTS[p_key]
    total_price = p_data["price"] * amount
    kp_amount = f"{amount} {p_data['unit']}"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➖", callback_data=f"minus:{p_key}:{amount}"),
            InlineKeyboardButton(text=kp_amount, callback_data="ignore"),
            InlineKeyboardButton(text="➕", callback_data=f"plus:{p_key}:{amount}")
        ],
        [InlineKeyboardButton(text=f"🛒 Savatga qo'shish ({total_price:,} so'm)", callback_data=f"add:{p_key}:{amount}")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"remove:{p_key}")]
    ])

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("👋 Assalomu alaykum! 'Xajiboy mintay fish' botiga xush kelibsiz!\nMenudan tanlang:", reply_markup=main_menu)

@dp.message(F.text == "⬅️ Orqaga")
async def go_back(message: types.Message):
    await message.answer("Bosh menyu:", reply_markup=main_menu)

@dp.message(F.text == "🥤 Ichimliklar va Souslar")
async def show_drinks(message: types.Message):
    await message.answer("Ichimlik yoki sousni tanlang:", reply_markup=drinks_menu)

# 🍕 Mahsulot ko'rsatish
@dp.message(F.text.in_([p["name"] for p in PRODUCTS.values()]))
async def send_product_info(message: types.Message):
    p_key = get_key_by_name(message.text)
    p_data = PRODUCTS[p_key]
    
    caption_text = (
        f"🛒 <b>{html.escape(p_data['name'])}</b>\n"
        f"💵 Narxi: <b>{p_data['price']:,} so'm</b> / {p_data['unit']}\n\n"
        f"Miqdorini belgilang va savatga qo'shing:"
    )
    
    try:
        await message.answer_photo(
            photo=URLInputFile(p_data["photo"]),
            caption=caption_text,
            reply_markup=get_product_keyboard(p_key, amount=1),
            parse_mode="HTML"
        )
    except Exception:
        await message.answer(
            caption_text,
            reply_markup=get_product_keyboard(p_key, amount=1),
            parse_mode="HTML"
        )

# 🔄 Plus / Minus
@dp.callback_query(F.data.startswith("plus:") | F.data.startswith("minus:"))
async def calc_callback(call: types.CallbackQuery):
    action, p_key, current_amount = call.data.split(":")
    current_amount = int(current_amount)
    new_amount = current_amount + 1 if action == "plus" else max(1, current_amount - 1)
        
    if new_amount != current_amount:
        await call.message.edit_reply_markup(reply_markup=get_product_keyboard(p_key, new_amount))
    await call.answer()

# 🛒 Savatga qo'shish
@dp.callback_query(F.data.startswith("add:"))
async def add_to_cart(call: types.CallbackQuery, state: FSMContext):
    _, p_key, amount = call.data.split(":")
    user_data = await state.get_data()
    cart = user_data.get("cart", {})
    
    cart[p_key] = cart.get(p_key, 0) + int(amount)
    await state.update_data(cart=cart)
    
    p_data = PRODUCTS[p_key]
    await call.answer(f"✅ {p_data['name']} dan {amount} {p_data['unit']} savatga qo'shildi!")

# 🗑 O'chirish
@dp.callback_query(F.data.startswith("remove:"))
async def remove_product(call: types.CallbackQuery, state: FSMContext):
    _, p_key = call.data.split(":")
    user_data = await state.get_data()
    cart = user_data.get("cart", {})
    
    if p_key in cart:
        del cart[p_key]
        await state.update_data(cart=cart)
        await call.answer("🗑 Mahsulot savatdan o'chirildi.")
    else:
        await call.answer("Bu mahsulot savatingizda yo'q.")

# 🛒 Savatni ko'rish
@dp.message(F.text == "🛒 Savatni ko'rish / Rasmiylashtirish")
async def view_cart(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get("cart", {})
    
    if not cart:
        await message.answer("🛒 Savatingiz hozircha bo'sh.")
        return
        
    cart_msg = "🛒 <b>Savatingizdagi mahsulotlar:</b>\n\n"
    grand_total = 0
    
    for p_key, amount in cart.items():
        p_data = PRODUCTS[p_key]
        item_total = p_data["price"] * amount
        grand_total += item_total
        cart_msg += f"• <b>{html.escape(p_data['name'])}</b>: {amount} {p_data['unit']} x {p_data['price']:,} = <b>{item_total:,} so'm</b>\n"
        
    cart_msg += f"\n💳 <b>Jami (Obshiy summa): {grand_total:,} so'm</b>"
        
    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚖 Buyurtmani rasmiylashtirish", callback_data="checkout")],
        [InlineKeyboardButton(text="🔄 Savatni tozalash", callback_data="clear_cart")]
    ])
    await message.answer(cart_msg, reply_markup=confirm_kb, parse_mode="HTML")

@dp.callback_query(F.data == "clear_cart")
async def clear_cart(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(cart={})
    await call.message.edit_text("🛒 Savat tozalandi.")
    await call.answer()

@dp.callback_query(F.data == "checkout")
async def checkout(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(OrderState.waiting_for_phone)
    phone_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon yuborish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await call.message.answer("📞 Telefon raqamingizni yuboring yoki yozing:", reply_markup=phone_kb)
    await call.answer()

@dp.message(OrderState.waiting_for_phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    await state.set_state(OrderState.waiting_for_address)
    
    loc_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("📍 Yetkazib berish manzilini (yoki lokatsiyangizni) yuboring:", reply_markup=loc_kb)

@dp.message(OrderState.waiting_for_address)
async def get_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", {})
    phone = data.get("phone")
    user_name = html.escape(message.from_user.full_name)
    username = f"@{message.from_user.username}" if message.from_user.username else "Yo'q"
    
    cart_str = ""
    grand_total = 0
    for p_key, amt in cart.items():
        p_data = PRODUCTS[p_key]
        item_total = p_data["price"] * amt
        grand_total += item_total
        cart_str += f"- {html.escape(p_data['name'])}: {amt} {p_data['unit']} x {p_data['price']:,} = {item_total:,} so'm\n"
        
    admin_msg = (
        "🚨 <b>YANGI BUYURTMA (Xajiboy mintay fish)</b> 🚨\n\n"
        f"👤 <b>Mijoz:</b> {user_name} ({username})\n"
        f"📞 <b>Telefon:</b> {html.escape(str(phone))}\n\n"
        f"🛍 <b>Buyurtma ro'yxati:</b>\n{cart_str}\n"
        f"💰 <b>Jami summa:</b> {grand_total:,} so'm"
    )
    
    # ADMIN_IDS ro'yxatidagi barcha adminlarga yuborish
    for admin_id in ADMIN_IDS:
        try:
            if message.location:
                await bot.send_message(admin_id, admin_msg + "\n📍 <b>Manzil:</b> Lokatsiya pastda👇", parse_mode="HTML")
                await bot.send_location(admin_id, latitude=message.location.latitude, longitude=message.location.longitude)
            else:
                await bot.send_message(admin_id, admin_msg + f"\n📍 <b>Manzil:</b> {html.escape(message.text)}", parse_mode="HTML")
        except Exception as e:
            logging.error(f"Admin {admin_id} ga xabar yuborishda xatolik: {e}")

    # Mijozga tasdiq xabari
    await message.answer(
        "✅ Xaridingiz uchun rahmat! Buyurtma restoranga ketdi, o‘zlari siz bilan aloqaga chiqishadi.",
        reply_markup=main_menu
    )
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
