import asyncio
import requests
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.filters import Command

TOKEN = "7931429720:AAHR_3wwS16YHjZe9Uvt-5sjKEsgDQzpSEE"


bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start_handler(message: Message):
    # вывод кнопок снизу
    keyboard = ReplyKeyboardMarkup (
        keyboard=[
            [KeyboardButton(text='Перезапустить бота')],
            [KeyboardButton(text='Показать список')],
            [KeyboardButton(text='Инструкция')],
            [KeyboardButton(text='Мой профиль')]
        ],
        resize_keyboard=True
    )

    # привествие
    first_name = message.from_user.first_name
    try:
        start_photo = 'https://i.pinimg.com/1200x/b8/d7/a0/b8d7a04e63e7f25ecb9a572ddc9cb464.jpg'
    except:
        start_photo = FSInputFile('start_Mark_photo.jpg')
    await message.answer_photo(start_photo,
caption=f'''
<b>Привет, {first_name}! </b>\n
Это — бот задачник с полноценной базой данных! <i>Короче тут пока очень сырая темка. Я тестирую бота привязанного к бекенду.</i> ладно, короче, вот команды:
- `/start` Запустить бота
- `/user` показывает твой id`шник и имя
- `/add задача` сохраняет задачу с ID пользователя в бд
- `/list` показывает только задачи этого пользователя.
- `/done id` пометить что-то верным
- `/delete id` удалить задачу по номеру.\n
Для удобства созданы ниже кнопки для работы с ботом. Команды и кнопки работают вместе. Поддержки или менеджера здесь нет поэтому звонить и жаловаться вам не кому.\n
<b>Нужна инструкция?</b>
Команда `/help` или кнопка ниже.
''',
parse_mode="HTML",
reply_markup=keyboard)


# ===================================================================================
# КОМАНДЫ /list, /help, /profile
# ===================================================================================

@dp.message(Command('list'))
async def list_handler(message: Message):
    user_id = message.from_user.id
    response = requests.get('http://localhost:8000/tasks', params={"user_id": user_id})
    data = response.json()
    if not data:
        await message.answer('У тебя нет задач')
        return
    text = ''
    for task in data:
        if task[3] == 1:
            status = '✅'
        else:
            status = '🚫'
        text += f'{status}| primary key: {task[0]} | {task[2]}\n'
    await message.answer(f'Твои задачи: \n\n{text}')

@dp.message(Command('help'))
async def help_handler(message: Message):
    await message.answer('''
<b>Инструкция:</b>
- `/start` Запустить бота
- `/user` показывает твой id`шник и имя
- `/add задача` сохраняет задачу с ID пользователя в бд
- `/list` показывает только задачи этого пользователя.
- `/done id` пометить что-то верным
- `/delete id` удалить задачу по номеру.
''', parse_mode='HTML')
@dp.message(Command('user'))
async def user_handler(message: Message):
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name
    username = message.from_user.username
    user_photos = await bot.get_user_profile_photos(user_id)

    text = f'''<b>Твой профиль</b>\n
- Твой личный id на платформе: {user_id}
- Твое имя: {user_first_name}
- Твой username: @{username}'''

    if user_photos.total_count == 0:
        await message.answer(text, parse_mode="HTML")
    else:
        photo = user_photos.photos[0][-1] # особенность аватарок. выбераем самую большую
        await message.answer_photo(
            photo.file_id,
            caption=text, 
            parse_mode="HTML"
        )

# ===================================================================================
# РАБОТА ПО ТОМУ ЧТО ОПРЕДЕЛЯЕМ КНОПКИ "ПЕРЕЗАПУСТИТЬ БОТА", "ПОКАЗАТЬ СПИСОК", "ИНСТРУКЦИЯ", "МОЙ ПРОФИЛЬ"
# ===================================================================================

@dp.message(lambda message: message.text =='Перезапустить бота')
async def start_button(message: Message):
    await start_handler(message)

@dp.message(lambda message: message.text == 'Показать список')
async def list_button(message:Message):
    await list_handler(message)

@dp.message(lambda message: message.text == 'Инструкция')
async def help_button(message: Message):
    await help_handler(message)

@dp.message(lambda message: message.text == 'Мой профиль')
async def user_button(message: Message):
    await user_handler(message)

# ===================================================================================
# ===================================================================================

@dp.message(Command('add'))
async def add_handler(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer('Правильный формат `/add Текст_Задачи`')
        return

    user_id = message.from_user.id
    task = parts[1]
    response = requests.post('http://localhost:8000/tasks', params={"task": task, "user_id": user_id})
    data = response.json()

    if response.status_code == 200:
        await message.answer('Успешно братуха')

@dp.message(Command('done'))
async def done_handler(message: Message):
    parts = message.text.split()

    if len(parts) < 2:
        await message.answer("Используй: /done id")
        return

    user_id = message.from_user.id
    task_id = parts[1]
    
    response = requests.put(f"http://localhost:8000/tasks/{task_id}",
    params={"done": 1, "user_id": user_id})
    
    await message.answer(f"Задача {task_id} отмечена выполненной!")

# /delete id — бот удаляет через backend
@dp.message(Command('delete'))
async def delete_handler(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Используй: /delete id")
        return
    
    task_id = parts[1]
    user_id = message.from_user.id
    
    response = requests.delete(
        f"http://localhost:8000/tasks/{task_id}", params={"user_id": user_id}
    )
    
    await message.answer(f"Задача {task_id} удалена!")

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())