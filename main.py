import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# SHU YERGA TOKENINGIZNI QO'YING (QO'SHTIRNOQLAR ORASIGA)
BOT_TOKEN = "8741646942:AAHUXnj7kHZk7-GuWweR3yklTbk3fd40TUQ"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

waiting_users = set()
active_pairs = {}

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔍 Suhbatdosh izlash")]],
        resize_keyboard=True
    )

def get_chat_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Suhbatni tugatish")]],
        resize_keyboard=True
    )

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id in active_pairs:
        await message.answer("Siz hozir suhbatdasiz.", reply_markup=get_chat_keyboard())
        return
    await message.answer(
        "👋 Anonim suhbat botiga xush kelibsiz!\n\nSuhbatdosh topish uchun pastdagi tugmani bosing.",
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

    if waiting_users:
        partner_id = waiting_users.pop()
        active_pairs[user_id] = partner_id
        active_pairs[partner_id] = user_id

        await bot.send_message(user_id, "🎉 Suhbatdosh topildi! Xabar yuborishingiz mumkin.", reply_markup=get_chat_keyboard())
        await bot.send_message(partner_id, "🎉 Suhbatdosh topildi! Xabar yuborishingiz mumkin.", reply_markup=get_chat_keyboard())
    else:
        waiting_users.add(user_id)
        await message.answer("🔍 Suhbatdosh izlanmoqda... Biroz kuting.", reply_markup=ReplyKeyboardRemove())

@dp.message(F.text == "❌ Suhbatni tugatish")
async def stop_chat(message: types.Message):
    user_id = message.from_user.id
    if user_id in waiting_users:
        waiting_users.remove(user_id)
        await message.answer("Qidiruv bekor qilindi.", reply_markup=get_main_keyboard())
        return

    if user_id in active_pairs:
        partner_id = active_pairs.pop(user_id)
        active_pairs.pop(partner_id, None)

        await message.answer("Suhbat yakunlandi.", reply_markup=get_main_keyboard())
        await bot.send_message(partner_id, "Suhbatdosh muloqotni tugatdi.", reply_markup=get_main_keyboard())
    else:
        await message.answer("Siz hozir hech kim bilan suhbatlashmayapsiz.", reply_markup=get_main_keyboard())

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
        await message.answer("Suhbatdosh topish uchun tugmani bosing.", reply_markup=get_main_keyboard())

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
