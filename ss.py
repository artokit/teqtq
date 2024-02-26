import asyncio
import time

from aiogram import Bot, Dispatcher, executor
from aiogram.utils.exceptions import BadRequest

import db_api

bot = Bot('6915856389:AAF1M7NWMIXVz5rGWKaMfO5cQFhKbMc1DY0')


async def main():
    f = open('log.txt', 'a')
    for i in range(200, 10_000):
        print(i, file=f)
        try:
            time.sleep(2)
            msg = await bot.send_message(text='t', chat_id=-1002110341139, message_thread_id=i)
            db_api.add_user(msg.reply_to_message.forum_topic_created.name)
            print(i, 'В БД', file=f)
        except Exception as e:
            print(i, 'Ошибка: ', str(e), file=f)

loop = asyncio.get_event_loop()
tasks = [loop.create_task(main())]
loop.run_until_complete(asyncio.wait(tasks))