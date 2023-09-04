from aiogram import Bot, executor, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import get_page, get_price
from datetime import datetime
from tk import BOT_TOKEN
import requests, os, asyncio

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot, storage=storage)

gearbox_keyboard = ReplyKeyboardMarkup()
for i in get_page.gearbox_converter.keys():
    gearbox_keyboard.add(KeyboardButton(i))

fueltype_keyborad = ReplyKeyboardMarkup()
for i in get_page.fueltype_list:
    fueltype_keyborad.add(KeyboardButton(i))


class AnalyzForm(StatesGroup):
    mark = State()
    model = State()
    oddmeter = State()
    engine_V = State()
    gearbox_type = State()
    years = State()
    fueltype = State()

async def analyze_data(message, data):
    await message.answer('Сбор данных окончен. Начинаем анализ ...')
    try:
        car = get_price.PriceAnalyzer(mark=data['mark'], model=data['model'], fueltype=data['fueltype'])
    except get_price.NotExistCarsError as nece:
        await message.answer(nece.message)

    except get_price.ElectroCarError as ece:
        await message.answer(ece.message)
    
    else:
        result = car.get_predict(input_data=[data['oddmeter'], data['engine_V'], data['gearbox_type'], data['years']])
        await message.answer(f'{round(result[0], 2)} - рекомендуемая цена ')


@dp.message_handler(commands=['start'], state='*')
async def simple_message(message):
    await message.answer('Привет, этот бот может посоветовать вам по какой цене лучше выставить свой автомобиль на основе уже существующих предложений на рынке по вашей модели')
    await message.answer('ВНИМАНИЕ: Бот не обрабатывает електромобили')
    await message.answer('Пожалуста сейчас ответье на заданные вопросы, если есть список для выбора, выберите из него. Примечание: если вы ввели какой-то параметр неправильно, нажмите /start и начните сначала')
    await message.answer('Вопрос 1. Фирма автомобиля (на английском)?')
    await AnalyzForm.mark.set()

@dp.message_handler(lambda msg: msg.text.isascii(), state=AnalyzForm.mark)
async def mark_question(message, state):
    async with state.proxy() as data:
        data['mark'] = message.text
    
    await message.answer('Вопрос 2. Модель автомобиля (на английском)?')
    await AnalyzForm.next()


@dp.message_handler(lambda msg: msg.text.isascii(), state=AnalyzForm.model)
async def model_question(message, state):
    async with state.proxy() as data:
        data['model'] = message.text
    
    await message.answer('Вопрос 3. Пробег автомобиля (в км)?')
    await AnalyzForm.next()


@dp.message_handler(lambda msg: msg.text.isdigit(), state=AnalyzForm.oddmeter)
async def oddmeter_question(message, state):
    async with state.proxy() as data:
        data['oddmeter'] = int(message.text)

    await message.answer('Вопрос 4. Обьем двигателя (в литрах)?')
    await AnalyzForm.next()

@dp.message_handler(lambda msg: msg.text.replace('.', '', 1).isdigit(), state=AnalyzForm.engine_V)
async def engine_v_question(message, state):
    async with state.proxy() as data:
        data['engine_V'] = float(message.text)
    
    await message.answer('Вопрос 5. Какая у вас коробка передач (выбрать из списка)?', reply_markup=gearbox_keyboard)
    await AnalyzForm.next()

@dp.message_handler(lambda msg: msg.text in list(get_page.gearbox_converter.keys()), state=AnalyzForm.gearbox_type)
async def gearbox_question(message, state):
    async with state.proxy() as data:
        data['gearbox_type'] = get_page.gearbox_converter[message.text]
    
    await message.answer('Вопрос 6. Какого года модель вашего авто (например 2014)?', reply_markup=ReplyKeyboardRemove())
    await AnalyzForm.next()

@dp.message_handler(lambda msg: msg.text.isdigit(), state=AnalyzForm.years)
async def year_question(message, state):

    async with state.proxy() as data:
        data['years'] = datetime.now().year - int(message.text)
    
    await message.answer('Теперь последний вопрос 7. Тип бензина для двигателя (выбрать из списка)?', reply_markup=fueltype_keyborad)
    await AnalyzForm.next()

@dp.message_handler(lambda msg: msg.text in get_page.fueltype_list, state=AnalyzForm.fueltype)
async def fueltype_question(message, state):

    async with state.proxy() as data:
        await state.finish()
        data['fueltype'] = message.text
        data['mark'] = data['mark'].replace(' ', '-').lower()
        data['model'] = data['model'].replace(' ', '-').lower()
        response = requests.get('{}/{}/{}/'.format(get_page.site_url ,data['mark'], data['model']))
    
        if response.status_code == 200:
            await message.answer('Вопросы окончены и получены. Начинаем обработку ...')
            if os.path.isfile('{}/{}_{}.json'.format(get_page.parser_path,  data['mark'], data['model'])):
                await analyze_data(message, data)

            else:
                get_page.get_file(start=1, file_dir='parser', mark=data['mark'], model=data['model'])
                await analyze_data(message, data)
                       
        else:
            await messgae.answer('Марка или модель автомобиля введены неправильно, пожалуйста перевведите данные', reply_markup=ReplyKeyboardRemove())
        
async def delete_old_json_files():
    dir_path = get_page.parser_path
    while True:
        # Получаем список файлов в директории, сортируем по времени создания
        files = sorted(os.listdir(dir_path), key=lambda f: os.path.getctime(os.path.join(dir_path, f)))

        # Оставляем только файлы с расширением .json и удаляем остальные
        for file in files[:-1]:
            if file.endswith('.json'):
                file_path = os.path.join(dir_path, file)
                os.remove(file_path)
                print(f"Файл {file} удален")

        await asyncio.sleep(600)  # Подождать 10 min



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(delete_old_json_files())
    executor.start_polling(dp, skip_updates=True)
    