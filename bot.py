import asyncio
import requests
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from config import TOKEN 

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_states = {} # режим состояния (создание)

@dp.message(Command('start'))
async def start_handler(message: Message):
    # вывод кнопок снизу
    keyboard = ReplyKeyboardMarkup (
        keyboard=[
            # [KeyboardButton(text='Перезапустить бота')],
            [KeyboardButton(text='Список задач')],
            [KeyboardButton(text='Команды')],
            [KeyboardButton(text='Мой профиль')]
        ],
        resize_keyboard=True
    )

    # привествие
    first_name = message.from_user.first_name
    caption = f'''
<b>Привет, {first_name}! </b>\n
Это — бот задачник с полноценной базой данных! <i>Короче тут пока очень сырая темка. Я тестирую бота привязанного к бекенду.</i> ладно, короче, вот команды:
• `/start` Запустить бота
• `/list` показывает только задачи этого пользователя.
• `/add задача` сохраняет задачу с ID пользователя в бд
• `/edit id` изменить задачу по номеру
• `/delete id` удалить задачу по номеру
• `/user` показывает твой id`шник и имя\n
Для удобства созданы ниже кнопки для работы с ботом. Команды и кнопки работают вместе. Поддержки или менеджера здесь нет поэтому звонить и жаловаться вам не кому.\n
<b>Нужна инструкция?</b>
Команда `/help` или кнопка ниже.
'''

    try:
        start_photo = 'https://i.pinimg.com/1200x/b8/d7/a0/b8d7a04e63e7f25ecb9a572ddc9cb464.jpg'
        await message.answer_photo(start_photo,
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard
        )
    except:
        start_photo = FSInputFile('start_Mark_photo.jpg')
        await message.answer_photo(start_photo,
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard
        )


# ===================================================================================
# ВСПОМОГАТЕЛЬНОЕ
# ===================================================================================

def get_tasks(user_id): #обращение к бэкенду как requests.get('.../tasks', params={...}). 
    # возравщает либо json либо None
    try:
        respone = requests.get(
            'http://localhost:8000/tasks',
            params={'user_id': user_id},
            timeout=5
        )
        if respone.status_code == 200:
            return respone.json()
        else:
            print(f'Ошибка при запросе к backend: {respone.status_code}') # вывести в терминал
            return None
    except (requests.ConnectionError, requests.Timeout):
        return None

def add_task(user_id, task):
    """Добавить задачу. Возвращает True/False."""
    try:
        response = requests.post(
            'http://localhost:8000/tasks',
            params={'task': task, 'user_id': user_id},
            timeout=5
        )
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False

def delete_task(task_id, user_id):
    """Удалить задачу. Возвращает True/False."""
    try:
        response = requests.delete(
            f'http://localhost:8000/tasks/{task_id}',
            params={'user_id': user_id},
            timeout=5
        )
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False

def update_status(task_id, user_id, done):
    """Изменить статус. Возвращает True/False."""
    try:
        response = requests.put(
            f'http://localhost:8000/tasks/{task_id}',
            params={'done': done, 'user_id': user_id},
            timeout=5
        )
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False

def update_text(task_id, user_id, new_text):
    """Изменить текст. Возвращает True/False."""
    try:
        response = requests.put(
            f'http://localhost:8000/tasks/{task_id}/text',
            params={'task': new_text, 'user_id': user_id},
            timeout=5
        )
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False

# ===================================================================================
# КОМАНДЫ /list, /help, /profile
# ===================================================================================

@dp.message(Command('list'))
async def list_handler(message: Message):
    user_id = message.from_user.id
    tasks = get_tasks(user_id)

    if tasks is None:
        await message.answer('Сервер недоступен. Попробуйте позже.')
        return

    if not tasks:
        await message.answer('У тебя нет задач')
        return
    
    text = ''

    for i,task in enumerate(tasks):
        if task[3] == 1:
            status = '✅'
        else:
            status = '🚫'
        text += f'{status}| {i + 1}. {task[2]}\n'

    await message.answer(f'<b>Твои задачи:</b>\n\n{text}', parse_mode='HTML')

@dp.message(Command('help'))
async def help_handler(message: Message):
    await message.answer('''
<b>Полные команды:</b>\n
<b>Работа с задачами</b>
• `/list` показывает только задачи этого пользователя.
• `/add задача` сохраняет задачу с ID пользователя в бд
• `/edit id` изменить задачу по номеру
• `/delete id` удалить задачу по номеру\n
<b>Личные команды</b>
• `/start` запустить бота
• `/user` увидеть профиль
''', parse_mode='HTML')
    
@dp.message(Command('user'))
async def user_handler(message: Message):
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name
    username = message.from_user.username
    user_photos = await bot.get_user_profile_photos(user_id)
    len_tasks = 0
    yes_amount = 0
    no_amount = 0

    tasks = get_tasks(user_id)
    if tasks is None:
        len_tasks = '<s>backend error</s>'
        yes_amount = '<s>backend error</s>'
        no_amount = '<s>backend error</s>'
    else: 
        len_tasks = len(tasks)
        for task in tasks:
            if task[3] == 0:
                no_amount += 1
            elif task[3] == 1:
                yes_amount += 1

    text = f'''<b>Твой профиль</b>\n
<b>Информация на платформе:</b>\n
• 📋 Количество твоих задач: {len_tasks}
• ✅ Количество выполненых: {yes_amount}
• Твой личный id на платформе: {user_id}\n
Твое имя: {user_first_name}
Твой username: @{username}'''

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

@dp.message(lambda message: message.text == 'Список задач')
async def list_button(message:Message):
    await list_handler(message)

@dp.message(lambda message: message.text == 'Команды')
async def help_button(message: Message):
    await help_handler(message)

@dp.message(lambda message: message.text == 'Мой профиль')
async def user_button(message: Message):
    await user_handler(message)

# ===================================================================================
# ===================================================================================

@dp.message(Command('list_developer'))
async def list_handler_developer(message: Message):
    try: # тут использую ручную обработку а не функцией тк это не что то обычное.
        response = requests.get('http://localhost:8000/tasks/developer')
        if response.status_code == 200:
            tasks = response.json()
        else:
            await message.answer(f"Ошибка сервера: {response.status_code}")
            return
    except requests.ConnectionError:
        await message.answer("Сервер недоступен. Попробуй позже.")
        return
        
    if not tasks:
        await message.answer('Задач нет в системе')
        return
    
    text = ''

    for i,task in enumerate(tasks):
        if task[3] == 1:
            status = '✅'
        else:
            status = '🚫'
        text += f'{status}| primary key: {task[0]} | user_id: {task[1]} | number: {i + 1} | {task[2]}\n'

    await message.answer(f'<b>Твои задачи:</b>\n\n{text}', parse_mode='HTML')

@dp.message(Command('add'))
async def add_handler(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer('Правильный формат `/add Текст_Задачи`')
        return

    user_id = message.from_user.id
    task = parts[1]

    if add_task(user_id, task):
        await message.answer('Успешно братуха')
    else: 
        await message.answer('Сервер не отвечает!')

@dp.message(Command('edit')) # 
async def done_handler(message: Message):
    # делим на парты
    parts = message.text.split()
    # проверяем чтобы партов было не менее двух
    if len(parts) < 2:
        await message.answer("Используй: /edit id")
        return
    # проверка + берем грязный айдишник
    try:
        num = int(parts[1])
    except ValueError:
        await message.answer('Введи номер!')
        return
    # получаем данные
    user_id = message.from_user.id
    tasks = get_tasks(user_id)
    if tasks is None:
        await message.answer('Сервер не отвечает! Попробуйте позже.')
        return
    # проверка что корректное (типо не меньше 1 и находится в промежутке кол-ве задач типа)
    if num < 1 or num > len(tasks):
        await message.answer('Неправильный номер задачи')
        return

    task = tasks[num - 1]
    task_id = task[0] # РЕАЛЬНЫЙ номер задачи получили 
    if task[3] == 0:
        status = '🚫 Не выполнено'
    else: 
        status = '✅ Выполнено'

    #готовим менюшку
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Изменить статус', callback_data=f'edit_status_{task_id}')],
            [InlineKeyboardButton(text='Изменить задачу', callback_data=f'edit_text_{task_id}')]
        ]
    )
    await message.answer(f'''
Изменение задачи по выбору. \n
Задача: {task[2]}
Статус: {status}

Выберите действие: 
''', reply_markup=keyboard)

# Обработка — через callback_query
@dp.callback_query()
async def callback_handler(callback):
    # получаем
    data = callback.data

    # разбираем
    parts = data.split('_') # изначальный формат 'edit_status_{task_id}'
    action = parts[0] # "edit" или "status" в случае если был сначала "edit" и мод "статус"
    mode = parts[1] # "text" или "status" / "1" "0"
    task_id = int(parts[2])

    if action == 'edit':

        if mode == 'status':
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                   [InlineKeyboardButton(text='✅', callback_data=f'status_1_{task_id}')],
                    [InlineKeyboardButton(text='🚫', callback_data=f'status_0_{task_id}')]
            ]
            )
            await callback.message.answer('Выбери действие:', reply_markup=keyboard)

        elif mode == 'text':
            user_states[callback.from_user.id] = {
                'action': "edit_text",
                "task_id": task_id
            }
            await callback.message.answer('Введи новый текст задачи:')

    elif action == 'status':
        done = int(mode) # так как если action статус то предпологается что там будет еще одна часть с номером
        if update_status(task_id, callback.from_user.id, done):
            if done == 1:
                status = '✅'
            elif done == 0:
                status = '🚫'
            await callback.message.answer(f'Отметка задачи была поменена: {status}')
        else: 
            await callback.message.answer('Сервер не отвечает.')

# /delete id — бот удаляет через backend
@dp.message(Command('delete'))
async def delete_handler(message: Message):
    # делим сообщение пользователя
    parts = message.text.split()
    # проверяем чтобы кол-во было не менее 2
    if len(parts) < 2:
        await message.answer("Используй: /delete id")
        return
    # проверка + берем айдишник сообщения (но он пока грязный)
    try:
        num = int(parts[1])
    except ValueError:
        await message.answer('Ввведи номер!')
        return
    # берем данные
    user_id = message.from_user.id
    tasks = get_tasks(user_id) # настоящие задачи пользователя (праймеры кеи настоящие)
    if tasks is None:
        await message.answer('Сервер не отвечает! Попробуйте позже.')
        return
    # проверка что корректное чилсо
    if num < 1 or num > len(tasks):
        await message.answer('Неправильный номер задачи.')
        return

    task_id = tasks[num - 1][0]
    if delete_task(task_id, user_id):
        await message.answer(f"Задача {num} удалена!")
    else:
        await message.answer('Сервер не отвечает.')

@dp.message()
async def state_handler(message: Message):
    user_id = message.from_user.id

    if user_id in user_states:
        state = user_states[user_id] # есть некий список который создался еще в обработке кнопок.

        if state['action'] == 'edit_text':
            new_text = message.text
            task_id = state['task_id']

            if update_text(task_id, user_id, new_text):
                await message.answer('Текст задачи изменен!')
            else:
                await message.answer('Сервер не отвеает.')

            # убрать состояние к чертям
            del user_states[user_id]
            return
    await message.answer(message.text)

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())