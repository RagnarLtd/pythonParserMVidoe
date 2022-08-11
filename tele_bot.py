import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton
from aiogram.utils.markdown import hbold, hlink
from main import get_data
from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    """ Создание клавиатуры с товарами и оправка ее пользователю """
    start_buttons = ['Клавиатуры', 'Мышки', 'Видеокарты', 'Процессоры', 'Мониторы']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer('Выбери товар', reply_markup=keyboard)


@dp.message_handler(Text(equals=['Клавиатуры', 'Мышки', 'Видеокарты', 'Процессоры', 'Мониторы']))
async def get_discount_mouse(message: types.Message):
    """ В зависимости от ответа пользователя,делается запрос на сайт Мвидео по определенному товару. По результатам
    пользователю выводится инлайн клавиатура с выбором производителя """
    products = {
        'Мышки': 183,
        'Клавиатуры': 217,
        'Видеокарты': 5429,
        'Процессоры': 5431,
        'Мониторы': 101,
    }
    msg = await message.answer('Пожалуйста подождите...')

    result = get_data(products[message.text])
    if result:
        with open('result/result.json') as file:
            data = json.load(file)

        keyboard_2 = types.InlineKeyboardMarkup(row_width=4, resize_keyboard=True)
        set_for_keyboard_2 = set()
        list_for_keyuboard_2 = list()
        for items in data.values():
            products = items.get('body').get('products')

            for item in products:
                set_for_keyboard_2.add(item.get('brandName'))
        for brand in set_for_keyboard_2:
            list_for_keyuboard_2.append(InlineKeyboardButton(text=f'{brand}', callback_data=f'{brand}'))
        keyboard_2.add(*list_for_keyuboard_2)
        await msg.delete()
        await message.answer('Выбери производителя', reply_markup=keyboard_2)
    else:
        await msg.delete()
        await message.answer('Нет скидок на данный товар')


@dp.callback_query_handler(lambda call: call.data)
async def process_callback_button1(callback_query: types.CallbackQuery):
    """ В зависимости от выбора бренда, выводятся определнные товары. Также выводится повторно инлайн клавиатура для
    выбора произвыодителя."""
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()
    with open('result/result.json') as file:
        data = json.load(file)
    for items in data.values():
        products = items.get('body').get('products')
        for item in products:
            if item.get('brandName') == callback_query.data:
                item_info = f"{hlink(item.get('name'), item.get('link'))}\n" \
                            f"{hbold('Цена: ')} {item.get('base_price')}\n" \
                            f"{hbold('Цена со скидкой: ')} {item.get('sale_price')}"
                await bot.send_message(callback_query.from_user.id, item_info)
    await bot.send_message(callback_query.from_user.id, text='Выбери производителя',
                           reply_markup=callback_query.message.reply_markup)


def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
