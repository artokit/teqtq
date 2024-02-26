from typing import Union
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import (Message, ContentTypes, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery,
                           MediaGroup, InputFile)
from db_api import get_users


dp: Union[None | Dispatcher] = None
ADMINS = [5833820044, 1917424026, 338406304]


def get_ids():
    return [i[0] for i in get_users()]


class SenderKeyboards:
    @staticmethod
    def cancel_or_not():
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Начать рассылку', callback_data='start_send'))
        keyboard.add(InlineKeyboardButton('Отмена', callback_data='not_start_send'))
        return keyboard

    @staticmethod
    def stop_urls():
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Остановить получение ссылок', callback_data='urls_stop'))
        return keyboard

    @staticmethod
    def without_text():
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('В рассылке не нужен текст', callback_data='without_text'))
        return keyboard

    @staticmethod
    def no_media():
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Поставить ссылки', callback_data='set_urls'))
        return keyboard


class SenderStates(StatesGroup):
    send_media = State()
    send_caption = State()
    send_urls = State()
    final = State()


def set_bot(d: Dispatcher):
    global dp
    dp = d


async def builder(data, ids):
    urls_keyboard = None
    caption = data.get('caption')
    if data.get('urls'):
        urls_keyboard = InlineKeyboardMarkup()
        for i in data.get('urls'):
            urls_keyboard.add(InlineKeyboardButton(i[0], url=i[1]))

    if data.get('media'):
        media = MediaGroup()
        first = True
        if len(data.get('media')) > 1:
            for i in data.get('media'):
                if i[0] == 'photo':
                    media.attach_photo(i[1], caption if first else None)
                if i[0] == 'video':
                    media.attach_video(InputFile(i[1]), caption if first else None)
                first = False
            for i in ids:
                try:
                    await dp.bot.send_media_group(i, media=media)
                except Exception as e:
                    print(str(e))

        if len(data.get('media')) == 1:
            d = data.get('media')[0]

            if d[0] == 'photo':
                for i in ids:
                    try:
                        await dp.bot.send_photo(i, d[1], caption=caption, reply_markup=urls_keyboard)
                    except Exception as e:
                        print(str(e))

            if d[0] == 'video':
                for i in ids:
                    try:
                        await dp.bot.send_video(i, d[1], caption=caption, reply_markup=urls_keyboard)
                    except Exception as e:
                        print(str(e))
        return

    else:
        for i in ids:
            try:
                await dp.bot.send_message(i, caption, reply_markup=urls_keyboard)
            except Exception as e:
                print(str(e))


def init_handlers():
    @dp.message_handler(commands=['send'], state='*')
    async def start_sender(message: Message, state: FSMContext):
        await state.finish()
        await state.reset_data()
        await SenderStates.send_caption.set()
        await message.answer('Отправьте текст для рассылки', reply_markup=SenderKeyboards.without_text())

    @dp.message_handler(state=SenderStates.send_media, content_types=ContentTypes.VIDEO)
    @dp.message_handler(state=SenderStates.send_media, content_types=ContentTypes.PHOTO)
    async def get_media(message: Message, state: FSMContext):
        data = await state.get_data()
        media = data.get('media', [])

        if message.video:
            media.append(['video', message.video.file_id])

        if message.photo:
            media.append(['photo', message.photo[-1].file_id])

        await state.update_data({'media': media})
        await message.answer(
            'Загружено. Если хотите поставить ссылки, то жмите на кнопку.\n'
            'Если хотите загрузить ещё другие фото/видео, то отправляйте их',
            reply_markup=SenderKeyboards.no_media()
        )

    @dp.callback_query_handler(lambda call: call.data == 'not_start_send', state=SenderStates.final)
    async def not_start(call: CallbackQuery, state: FSMContext):
        await state.finish()
        await state.reset_data()
        await call.message.answer('Действие отменено')

    @dp.callback_query_handler(lambda call: call.data == 'urls_stop', state=SenderStates.send_urls)
    async def send_message_for_test(call: CallbackQuery, state: FSMContext):
        await SenderStates.final.set()
        await call.message.answer('Вот выглядит рассылка сейчас: ')
        await builder(await state.get_data(), [call.message.chat.id, ])
        await call.message.answer('Отправляем?', reply_markup=SenderKeyboards.cancel_or_not())

    @dp.callback_query_handler(lambda call: call.data == 'without_text', state=SenderStates.send_caption)
    async def without_text(call: CallbackQuery):
        await SenderStates.send_media.set()
        await call.message.answer('Отправьте фотографию или видео')

    @dp.callback_query_handler(lambda call: call.data == 'start_send', state=SenderStates.final)
    async def start_send(call: CallbackQuery, state: FSMContext):
        await call.message.answer('Рассылка началась')
        data = await state.get_data()
        await state.finish()
        await state.reset_data()
        await builder(data, get_ids())

    @dp.callback_query_handler(lambda call: call.data == 'set_urls', state=SenderStates.send_media)
    async def get_urls(call: CallbackQuery):
        await SenderStates.send_urls.set()
        await call.message.answer(
            'Отправьте ссылки в таком формате:\n'
            'Текст Ссылки\n'
            'Ссылка',
            reply_markup=SenderKeyboards.stop_urls()
        )

    @dp.message_handler(state=SenderStates.send_urls)
    async def get_url(message: Message, state: FSMContext):
        data = await state.get_data()
        urls = data.get('urls', [])
        t = message.text.split('\n')
        urls.append([t[0], t[1]])
        await state.update_data({'urls': urls})
        await message.answer('Заканчиваем или ещё хотите ?', reply_markup=SenderKeyboards.stop_urls())

    @dp.message_handler(state=SenderStates.send_caption)
    async def get_caption(message: Message, state: FSMContext):
        await state.set_data({'caption': message.text})
        await SenderStates.send_media.set()
        await message.answer('Отправьте фотографию или видео', reply_markup=SenderKeyboards.no_media())
