from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import initiate_db, get_all_products, add_product


def populate_products():  # Добавляю продукты в таблицу

    add_product("Product1", "Описание 1", 100)
    add_product("Product2", "Описание 2", 200)
    add_product("Product3", "Описание 3", 300)
    add_product("Product4", "Описание 4", 400)

    print("Таблица Products успешно заполнена!")


# делаю базы данных и заполняю продуктами
initiate_db()
populate_products()

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
kb.add(button)
kb.add(button2)
kb.add(button3)

catalog_kb = InlineKeyboardMarkup()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Выберите опцию', reply_markup=kb)


@dp.message_handler(text="Купить")
async def get_buying_list(message: types.Message):
    products = get_all_products()
    if not products:
        await message.answer("Нет доступных продуктов.")
        return

    for product in products:
        product_id, title, description, price = product
        product_text = f'Название: {title} | Описание: {description} | Цена: {price}'
        await message.answer(product_text)
        await message.answer_photo(photo=open(f'{product_id}.jpeg', 'rb'))
        catalog_kb.add(InlineKeyboardButton(text=title, callback_data=f'product_{product_id}'))

    await message.answer('Выберите продукт для покупки:', reply_markup=catalog_kb)


@dp.callback_query_handler(lambda call: call.data.startswith('product_'))
async def send_confirm_message(call: types.CallbackQuery):
    product_id = call.data.split('_')[1]
    await call.answer('Вы выбрали продукт для покупки. Подтвердите покупку?', show_alert=True)
    confirm_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Подтвердить', callback_data=f'confirm_{product_id}')],
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_buying')]
        ]
    )
    await call.message.answer('Подтвердите покупку:', reply_markup=confirm_kb)


@dp.callback_query_handler(lambda call: call.data.startswith('confirm_'))
async def confirm_buying(call: types.CallbackQuery):
    await call.answer('Вы успешно приобрели продукт!')


@dp.callback_query_handler(text="cancel_buying")
async def cancel_buying(call: types.CallbackQuery):
    await call.answer('Покупка отменена.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
