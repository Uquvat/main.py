import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Bot tokeningizni kiriting
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = Bot(8741646942:AAHUXnj7kHZk7-GuWweR3yklTbk3fd40TUQ)
dp = Dispatcher()

# Navbatda turgan foydalanuvchilar ro'yxati (queue)
waiting_users = set()

# Ulangan juftliklar: {user_id: partner_id}
active_pairs = {}

# Tugmalar
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Suhbatdosh izlash")]
        ],
        resize_keyboard=True
    )

def get_chat_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Suhbatni tugatish")]
        ],
        resize_keyboard=True
    )

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    
    # Agar foydalanuvchi suhbatda bo'lsa
    if us er_id in active_pairs:
        await message.answer("Siz hozir suhbatdasiz.", reply_markup=get_chat_keyboard())
        return

    await message.answer(
        "👋 Anonim suhbat botiga xush kelibsiz!\n\n"
        "Suhbatdosh topish uchun pastdagi tugmani bosing.",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "🔍 Suhbatdosh izlash")
async def search_partner(message: types.Message):
    user_id = message.from_user.id

    if user_id in active_pairs:
        await message.answer("Siz allaqachon suhbatdasiz!", reply_markup=get_chat_keyboard())
        return

    if user_id in waiting_users:
        await message.answer("Qidiruv davom etmoqda, kuting...")
        return

    # Agar navbatda kimdir bo'lsa, ularni ulash
    if waiting_users:
        partner_id = waiting_users.pop()
        
        active_pairs[user_id] = partner_id
        active_pairs[partner_id] = user_id

        await bot.send_message(
            user_id, 
            "🎉 Suhbatdosh topildi! Xabar yuborishingiz mumkin.", 
            reply_markup=get_chat_keyboard()
        )
        await bot.send_message(
            partner_id, 
            "🎉 Suhbatdosh topildi! Xabar yuborishingiz mumkin.", 
            reply_markup=get_chat_keyboard()
        )
    else:
        # Navbatga qo'shish
        waiting_users.add(user_id)
        await message.answer(
            "🔍 Suhbatdosh izlanmoqda... Biroz kuting.", 
            reply_markup=ReplyKeyboardRemove()
        )

@dp.message(F.text == "❌ Suhbatni tugatish")
async def stop_chat(message: types.Message):
    user_id = message.from_user.id

    # Navbatda bo'lsa, navbatdan chiqarish
    if user_id in waiting_users:
        waiting_users.remove(user_id)
        await message.answer("Qidiruv bekor qilindi.", reply_markup=get_main_keyboard())
        return

    # Suhbatda bo'lsa, suhbatni yakunlash
    if user_id in active_pairs:
        partner_id = active_pairs.pop(user_id)
        active_pairs.pop(partner_id, None)

        await message.answer("Suhbat yakunlandi.", reply_markup=get_main_keyboard())
        await bot.send_message(
            partner_id, 
            "Suhbatdosh muloqotni tugatdi.", 
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer("Siz hozir hech kim bilan suhbatlashmayapsiz.", reply_markup=get_main_keyboard())

# Xabarlarni suhbatdoshga yo'naltirish (Text, Photo, Voice, Sticker va h.k.)
@dp.message()
async def forward_message(message: types.Message):
    user_id = message.from_user.id

    if user_id in active_pairs:
        partner_id = active_pairs[user_id]
        try:
            # Xabarni sherigiga asl nusxada ko'chirish
            await message.copy_to(chat_id=partner_id)
        except Exception:
            await message.answer("Xabarni yuborishda xatolik yuz berdi.")
    else:
        await message.answer("Suhbatdosh topish uchun tugmani bosing.", reply_markup=get_main_keyboard())

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
