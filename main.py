import os
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ChatJoinRequest, Message, ContentType
import db_api
import keyboards
from aiogram import Bot, Dispatcher, executor
from sender import set_bot, init_handlers

TOKEN = '6915856389:AAF1M7NWMIXVz5rGWKaMfO5cQFhKbMc1DY0'

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
set_bot(dp)
init_handlers()
MEDIA_PATH = os.path.join(os.path.dirname(__file__), 'media')


@dp.message_handler()
async def on_message(message: Message):
    print(message)


# asyncio.run(main())
# exit()

@dp.chat_join_request_handler()
async def start(update: ChatJoinRequest):
    db_api.add_user(update.from_user.id)
    await update.approve()
    await asyncio.sleep(5)
    await bot.send_message(update.from_user.id, '🔥Hola. Quieres que te enseñe a ganar dinero con Aviator?🔥')
    await asyncio.sleep(5)
    await bot.send_chat_action(update.from_user.id, 'typing')
    await asyncio.sleep(20)

    with open(os.path.join(MEDIA_PATH, 'video1.mp4'), 'rb') as f:
        await bot.send_video(
            update.from_user.id,
            f,
            caption='💰Los chicos de mi equipo están haciendo $100-$200 al día mínimo.\n'
                    'Listo para formar y unirse a mi equipo?'
        )
    await asyncio.sleep(10)
    await bot.send_chat_action(update.from_user.id, 'typing')
    await asyncio.sleep(10)
    await bot.send_message(
        update.from_user.id,
        '🤑¡Escríbeme en mensajes privados y te diré cómo ganar dinero!',
        reply_markup=keyboards.redirect_keyboard
    )


@dp.message_handler(content_types=ContentType.ANY)
async def any_message(message: Message):
    await message.answer(
        '🤑¡Escríbeme en mensajes privados y te diré cómo ganar dinero!',
        reply_markup=keyboards.redirect_keyboard
    )


executor.Executor(dp).start_polling(
    allowed_updates=["message", "inline_query", "chat_member", 'chat_join_request', 'callback_query']
)
