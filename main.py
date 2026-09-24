import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# ---------------- SOZLAMALAR ----------------
BOT_TOKEN = "8741646942:AAHUXnj7kHZk7-GuWweR3yklTbk3fd40TUQ"  # Bot tokeningiz
ADMIN_ID = 8523757446 # O'zingizning Telegram ID raqamingiz (masalan: 123456789)
# --------------------------------------------

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Ma'lumotlarni saqlash (Xotirada)
users_gender = {}  # {user_id: "O'g'il bola" / "Qiz bola"}
waiting_users = set()
active_pairs = {}

# Tugmalar
def get_gender_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👨 O'g'il bola"), KeyboardButton(text="👩 Qiz bola")]
        ],
        resize_keyboard=True
    )

def get_main_keyboard(user_id):
    buttons = [[KeyboardButton(text="🔍 Suhbatdosh izlash")]]
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton(text="📊 Admin Panel")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_chat_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Suhbatni tugatish")]],
        resize_keyboard=True
    )

def get_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📈 Statistika")],
            [KeyboardButton(text="📢 Barchaga xabar yuborish")],
            [KeyboardButton(text="⬅️ Bosh menyuga qaytish")]
        ],
        resize_keyboard=True
    )

# /start buyrug'i
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in active_pairs:
        await message.answer("Siz hozir suhbatdasiz.", reply_markup=get_chat_keyboard())
        return

    if user_id not in users_gender:
        await message.answer(
            "👋 Anonim chat botiga xush kelibsiz!\n\nIltimos, avval jinsingizni tanlang:",
            reply_markup=get_gender_keyboard()
        )
    else:
        await message.answer(
            "Muloqotni boshlash uchun quyidagi tugmani bosing:",
            reply_markup=get_main_keyboard(user_id)
        )

# Jinsni tanlash
@dp.message(F.text.in_({"👨 O'g'il bola", "👩 Qiz bola"}))
async def set_gender(message: types.Message):
    user_id = message.from_user.id
    users_gender[user_id] = message.text
    await message.answer(
        f"Rahmat! Jinsingiz ({message.text}) saqlandi.\n\nSuhbatdosh izlash uchun tugmani bosing:",
        reply_markup=get_main_keyboard(user_id)
    )

# Suhbatdosh izlash
@dp.message(F.text == "🔍 Suhbatdosh izlash")
async def search_partner(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in users_gender:
        await message.answer("Iltimos, avval jinsingizni tanlang:", reply_markup=get_gender_keyboard())
        return

    if user_id in active_pairs:
        await message.answer("Siz allaqachon suhbatdasiz!", reply_markup=get_chat_keyboard())
        return

    if user_id in waiting_users:
        await message.answer("Qidiruv davom etmoqda, kuting...")
        return

    if waiting_users:
        partner_id = waiting_users.pop()
        active_pairs[user_id] = partner_id
        active_pairs[partner_id] = user_id

        await bot.send_message(user_id, "🎉 Suhbatdosh topildi! Xabar yuborishingiz mumkin.", reply_markup=get_chat_keyboard())
        await bot.send_message(partner_id, "🎉 Suhbatdosh topildi! Xabar yuborishingiz mumkin.", reply_markup=get_chat_keyboard())
    else:
        waiting_users.add(user_id)
        await message.answer("🔍 Suhbatdosh izlanmoqda... Biroz kuting.", reply_markup=ReplyKeyboardRemove())

# Suhbatni tugatish
@dp.message(F.text == "❌ Suhbatni tugatish")
async def stop_chat(message: types.Message):
    user_id = message.from_user.id
    if user_id in waiting_users:
        waiting_users.remove(user_id)
        await message.answer("Qidiruv bekor qilindi.", reply_markup=get_main_keyboard(user_id))
        return

    if user_id in active_pairs:
        partner_id = active_pairs.pop(user_id)
        active_pairs.pop(partner_id, None)

        await message.answer("Suhbat yakunlandi.", reply_markup=get_main_keyboard(user_id))
        await bot.send_message(partner_id, "Suhbatdosh muloqotni tugatdi.", reply_markup=get_main_keyboard(partner_id))
    else:
        await message.answer("Siz hozir hech kim bilan suhbatlashmayapsiz.", reply_markup=get_main_keyboard(user_id))

# ---------------- ADMIN PANEL ----------------
@dp.message(F.text == "📊 Admin Panel")
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Admin panelga xush kelibsiz:", reply_markup=get_admin_keyboard())

@dp.message(F.text == "📈 Statistika")
async def show_stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        total_users = len(users_gender)
        boys = sum(1 for g in users_gender.values() if g == "👨 O'g'il bola")
        girls = sum(1 for g in users_gender.values() if g == "👩 Qiz bola")
        active_chats = len(active_pairs) // 2
        
        stat_text = (
            f"📊 **Bot statistikasi:**\n\n"
            f"👤 Jami foydalanuvchilar: {total_users} ta\n"
            f"👨 O'g'il bolalar: {boys} ta\n"
            f"👩 Qiz bolalar: {girls} ta\n"
            f"💬 Faol suhbatlar: {active_chats} ta\n"
            f"⏳ Qidiruvdagilar: {len(waiting_users)} ta"
        )
        await message.answer(stat_text, parse_mode="Markdown")

@dp.message(F.text == "📢 Barchaga xabar yuborish")
async def ask_broadcast_message(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Barchaga yubormoqchi bo'lgan xabaringizni `/send Matn` ko'rinishida yozib yuboring.\n\nMasalan:\n`/send Salom hammaga! Botimizda yangi imkoniyatlar qo'shildi.`")

@dp.message(F.text.startswith("/send "))
async def broadcast_message(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        text_to_send = message.text[6:]
        count = 0
        for uid in users_gender.keys():
            try:
                await bot.send_message(uid, text_to_send)
                count += 1
            except Exception:
                pass
        await message.answer(f"✅ Xabar {count} ta foydalanuvchiga yetkazildi.")

@dp.message(F.text == "⬅️ Bosh menyuga qaytish")
async def back_to_main(message: types.Message):
    await message.answer("Bosh menyu:", reply_markup=get_main_keyboard(message.from_user.id))

# Xabarlarni bir-biriga yetkazish
@dp.message()
async def forward_message(message: types.Message):
    user_id = message.from_user.id
    if user_id in active_pairs:
        partner_id = active_pairs[user_id]
        try:
            await message.copy_to(chat_id=partner_id)
        except Exception:
            await message.answer("Xabarni yuborishda xatolik yuz berdi.")
    else:
        await message.answer("Suhbatdosh topish uchun tugmani bosing.", reply_markup=get_main_keyboard(user_id))

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
