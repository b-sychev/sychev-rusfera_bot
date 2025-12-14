import sys
import random
import re
import logging
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Наши модули
from data_manager import add_request, get_request, load_requests, save_requests
from reminder import start_reminder_service

# Загрузка токена
try:
    from config import TOKEN
    print("✅ Токен бота загружен!")
except ImportError:
    print("❌ ОШИБКА: Создай файл config.py с токеном!")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/rusfera_surgut.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
SELECTING_SERVICE, DESCRIBING_PROBLEM, ENTERING_CONTACTS = range(3)

# ==================== КЛАВИАТУРЫ ====================
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🛠 Услуги"), KeyboardButton("💰 Цены")],
        [KeyboardButton("📝 Заявка"), KeyboardButton("📊 Статус")],
        [KeyboardButton("📍 Контакты"), KeyboardButton("❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_services_keyboard():
    keyboard = [
        [KeyboardButton("💻 Компьютеры"), KeyboardButton("🖨 Принтеры")],
        [KeyboardButton("🗄 Серверы"), KeyboardButton("🎮 Игровые ПК")],
        [KeyboardButton("🔙 Назад в меню")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard():
    keyboard = [[KeyboardButton("🔙 Отмена")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== ГЕНЕРАЦИЯ НОМЕРА ЗАЯВКИ ====================
def generate_request_number():
    date_str = datetime.now().strftime('%Y%m%d')
    number = random.randint(100, 999)
    return f"RUS-{date_str}-{number}"

# ==================== СОЗДАНИЕ ЗАЯВКИ ====================
def create_request_status(request_number, service_type, problem, contacts, user_name):
    statuses = ["Принята в обработку", "На диагностике", "Ожидает запчастей", "В ремонте", "Тестирование", "Готово к выдаче"]
    current_status = random.choice(statuses[:3])
    ready_date = datetime.now() + timedelta(days=random.randint(1, 7))
    
    request_data = {
        'number': request_number,
        'service_type': service_type,
        'problem': problem,
        'contacts': contacts,
        'user_name': user_name,
        'status': current_status,
        'created_date': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'ready_date': ready_date.strftime('%d.%m.%Y'),
        'master': random.choice(['Алексей Петров', 'Иван Сидоров', 'Михаил Козлов']),
        'master_phone': '+7 (900) 123-45-67'
    }
    
    # Сохраняем в JSON через data_manager
    add_request(request_data)
    return request_data

# ==================== ОБРАБОТЧИКИ КОМАНД ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = f"""
СЕРВИСНЫЙ ЦЕНТР "РУСФЕРА" (СУРГУТ)

Здравствуйте, {user.first_name}!

Наш адрес: г. Сургут, ул. Югорская д. 34.
Телефон: +7 (3462) 39 09 14
Режим работы: Пн-Пт 8:00-18:00, Сб 11:00-16:00

Основные услуги:
• Ремонт компьютеров и ноутбуков
• Заправка картриджей
• Обслуживание оргтехники
• IT-аутсорсинг для бизнеса

Выберите действие на панели ниже:
"""
    await update.message.reply_text(text, reply_markup=get_main_keyboard())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
ПОМОЩЬ И ПОДДЕРЖКА

Как пользоваться ботом:
1. Используйте кнопки меню для навигации
2. Или команды: /start, /help, /contacts

Наши услуги:
• Диагностика - бесплатно (при ремонте)
• Ремонт ПК/ноутбуков - от 1000 ₽
• Заправка картриджей - от 300 ₽
• Чистка от пыли - 800 ₽

Контакты для связи:
+7 (3462) 39 09 14
г. Сургут, ул. Югорская д. 34.
"""
    await update.message.reply_text(text)

async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
КОНТАКТЫ СЕРВИСНОГО ЦЕНТРА "РУСФЕРА"

Адрес офиса:
г. Сургут, ул. Югорская д. 34

Телефоны:
• Основной: +7 (3462) 39 09 14

Электронная почта:
• it@rusfera.ru

Режим работы:
Понедельник-Пятница: 8:00 - 18:00
Суббота: 11:00 - 16:00
Воскресенье: выходной
"""
    await update.message.reply_text(text)

async def show_services_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
ВЫБЕРИТЕ КАТЕГОРИЮ УСЛУГ:

💻 Компьютеры - ремонт ПК, ноутбуков
🖨 Принтеры - заправка, ремонт картриджей
🗄 Серверы - настройка, обслуживание
🎮 Игровые ПК - сборка, апгрейд

Нажмите на нужную категорию:
"""
    await update.message.reply_text(text, reply_markup=get_services_keyboard())

async def show_computer_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
РЕМОНТ КОМПЬЮТЕРОВ И НОУТБУКОВ:

• Диагностика - 500 ₽ (бесплатно при ремонте)
• Установка Windows - от 1500 ₽
• Чистка от пыли + замена термопасты - 1200 ₽
• Замена экрана ноутбука - от 3000 ₽
• Ремонт материнской платы - от 2500 ₽
• Восстановление данных - от 2000 ₽
• Замена клавиатуры ноутбука - от 1500 ₽
• Ремонт блока питания - от 1200 ₽

Для точного расчета:
Позвоните +7 (3462) 39 09 14
"""
    await update.message.reply_text(text)

async def show_printer_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
ПРИНТЕРЫ И КАРТРИДЖИ:

• Заправка картриджа - от 300 ₽
• Восстановление картриджа - от 500 ₽
• Ремонт принтера - от 1500 ₽
• Продажа картриджей - от 800 ₽
• Чистка печатающей головки - 1000 ₽

Обслуживаем:
HP, Canon, Epson, Xerox, Brother, Samsung
"""
    await update.message.reply_text(text)

async def show_server_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
ОБСЛУЖИВАНИЕ СЕРВЕРОВ:

• Настройка сервера - от 5000 ₽
• Обслуживание серверов - от 300 ₽/мес
• Почтовый сервер - 100 ₽/мес
• Резервное копирование - от 2000 ₽/мес
• Настройка VPN - от 2000 ₽
• Мониторинг серверов - от 1500 ₽/мес
"""
    await update.message.reply_text(text)

async def show_gaming_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
ИГРОВЫЕ СИСТЕМЫ:

• Сборка игрового ПК - от 25000 ₽
• Разгон процессора/видеокарты - от 2000 ₽
• Настройка игрового ПО - 1500 ₽
• Чистка игровых систем - 1500 ₽
• Апгрейд компонентов - от 5000 ₽
• Настройка подсветки RGB - 1000 ₽
"""
    await update.message.reply_text(text)

async def check_request_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ПРОВЕРКА СТАТУСА РЕМОНТА\n\n"
        "Для проверки статуса отправьте номер заявки.\n"
        "Номер имеет формат: RUS-XXXXXXXXX\n\n"
        "Пример: RUS-20251205-123\n\n"
        "Или отправьте ваше имя и телефон для поиска заявки."
    )

async def show_request_status(update: Update, context: ContextTypes.DEFAULT_TYPE, request_number):
    request = get_request(request_number)  # Теперь берём из data_manager
    if request:
        status_text = f"""
СТАТУС ЗАЯВКИ {request_number}

Тип техники: {request['service_type']}
Проблема: {request['problem']}
Контактное лицо: {request['user_name']}
Дата приема: {request['created_date']}

ТЕКУЩИЙ СТАТУС: {request['status']}

Информация по заявке:
• Ответственный мастер: {request['master']}
• Телефон мастера: {request['master_phone']}
• Ориентировочная готовность: {request['ready_date']}

По вопросам звоните: +7 (3462) 39 09 14
"""
    else:
        status_text = f"""
Заявка с номером {request_number} не найдена.

Для уточнения информации:
• Позвоните по телефону: +7 (3462) 39 09 14
• Назовите номер заявки или ФИО
• Рабочее время: Пн-Пт 8:00-18:00
"""
    await update.message.reply_text(status_text)

async def start_repair_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ОФОРМЛЕНИЕ ЗАЯВКИ НА РЕМОНТ\n\n"
        "Выберите тип техники:\n"
        "1. Компьютер/ноутбук\n"
        "2. Принтер/МФУ\n"
        "3. Сервер\n"
        "4. Игровой ПК\n"
        "5. Другое\n\n"
        "Отправьте номер или название типа техники",
        reply_markup=get_back_keyboard()
    )
    return SELECTING_SERVICE

async def select_service_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service_type = update.message.text
    
    if service_type == "🔙 Отмена":
        await update.message.reply_text("Оформление заявки отменено.", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    context.user_data['service_type'] = service_type
    await update.message.reply_text(
        f"Вы выбрали: {service_type}\n\n"
        "Теперь опишите проблему:\n"
        "• Что случилось с техникой?\n"
        "• Когда началась проблема?\n"
        "• Что уже пробовали сделать?\n\n"
        "Опишите подробно!",
        reply_markup=get_back_keyboard()
    )
    return DESCRIBING_PROBLEM

async def describe_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    problem = update.message.text
    
    if problem == "🔙 Отмена":
        await update.message.reply_text("Оформление заявки отменено.", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    context.user_data['problem'] = problem
    await update.message.reply_text(
        "Теперь укажите контактные данные:\n"
        "• Ваше имя\n"
        "• Номер телефона для связи\n\n"
        "Формат: Иван Петров, +7 (900) 123-45-67",
        reply_markup=get_back_keyboard()
    )
    return ENTERING_CONTACTS

async def enter_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contacts = update.message.text
    user = update.effective_user
    
    if contacts == "🔙 Отмена":
        await update.message.reply_text("Оформление заявки отменено.", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    request_number = generate_request_number()
    request_info = create_request_status(
        request_number,
        context.user_data.get('service_type', 'Не указан'),
        context.user_data.get('problem', 'Не указана'),
        contacts,
        user.first_name
    )
    
    summary = f"""
ВАША ЗАЯВКА ПРИНЯТА!

Номер заявки: {request_number}
Тип техники: {request_info['service_type']}
Проблема: {request_info['problem']}
Контактные данные: {contacts}
Дата оформления: {request_info['created_date']}

ТЕКУЩИЙ СТАТУС: {request_info['status']}

Что дальше:
1. В течение 30 минут с вами свяжется наш менеджер
2. Согласуем время диагностики
3. После диагностики сообщим точную стоимость

Для проверки статуса:
• Используйте кнопку "Статус" в меню
• Отправьте номер заявки: {request_number}
• Или позвоните: +7 (3462) 39 09 14
"""
    await update.message.reply_text(summary, reply_markup=get_main_keyboard())
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_repair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Оформление заявки отменено.", reply_markup=get_main_keyboard())
    context.user_data.clear()
    return ConversationHandler.END

# ==================== ГЛАВНЫЙ ОБРАБОТЧИК СООБЩЕНИЙ ====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user = update.effective_user
    
    # 1. Проверка на номер заявки (самое важное - должно быть первым!)
    request_pattern = r'RUS-\d{8}-\d{3}'
    match = re.search(request_pattern, user_text.upper())
    
    if match:
        request_number = match.group()
        await show_request_status(update, context, request_number)
        return
    
    # 2. Обработка кнопок меню
    if user_text == "🛠 Услуги" or user_text == "💰 Цены":
        await show_services_menu(update, context)
    elif user_text == "📝 Заявка":
        await start_repair_request(update, context)
        return SELECTING_SERVICE
    elif user_text == "📊 Статус":
        await check_request_status(update, context)
    elif user_text == "📍 Контакты":
        await contacts(update, context)
    elif user_text == "❓ Помощь":
        await help_cmd(update, context)
    elif user_text == "💻 Компьютеры":
        await show_computer_services(update, context)
    elif user_text == "🖨 Принтеры":
        await show_printer_services(update, context)
    elif user_text == "🗄 Серверы":
        await show_server_services(update, context)
    elif user_text == "🎮 Игровые ПК":
        await show_gaming_services(update, context)
    elif user_text == "🔙 Назад в меню":
        await update.message.reply_text("Возвращаемся в главное меню:", reply_markup=get_main_keyboard())
    
    # 3. Обработка общих фраз
    elif any(word in user_text.lower() for word in ['ремонт', 'починить', 'сломал', 'не работает']):
        response = """
ВЫ ХОТИТЕ ОФОРМИТЬ ЗАЯВКУ НА РЕМОНТ?

Для быстрого оформления:
1. Позвоните: +7 (3462) 39 09 14
2. Или используйте кнопку "Заявка" в меню
3. Или укажите тип техники и проблему

Мы перезвоним в течение 15 минут!
"""
        await update.message.reply_text(response, reply_markup=get_main_keyboard())
    elif any(word in user_text.lower() for word in ['цена', 'стоимость', 'сколько стоит']):
        await update.message.reply_text("Актуальные цены смотрите в разделе 'Услуги'", reply_markup=get_main_keyboard())
    elif any(word in user_text.lower() for word in ['адрес', 'телефон', 'контакты']):
        await contacts(update, context)
    elif any(word in user_text.lower() for word in ['статус', 'проверить заявку']):
        await check_request_status(update, context)
    elif any(word in user_text.lower() for word in ['привет', 'здравствуйте', 'добрый день']):
        await update.message.reply_text(f"Здравствуйте, {user.first_name}! Чем могу помочь?", reply_markup=get_main_keyboard())
    else:
        # 4. Ответ по умолчанию
        response = f"""
Спасибо за сообщение, {user.first_name}!

Ваш запрос: "{user_text}"

Для оперативной помощи:
• Выберите нужный раздел в меню ниже
• Или позвоните: +7 (3462) 39 09 14

Мы на связи Пн-Пт с 8:00 до 18:00!
"""
        await update.message.reply_text(response, reply_markup=get_main_keyboard())

# ==================== ЗАПУСК БОТА ====================
def main():
    print("=" * 50)
    print("ЗАПУСК БОТА ДЛЯ 'РУСФЕРА' (СУРГУТ)")
    print(f"Бот: @SurgutRusferaRubot")
    print(f"Токен: {TOKEN[:15]}...")
    print("=" * 50)
    
    try:
        app = Application.builder().token(TOKEN).build()
        
        repair_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex('^(📝 Заявка)$'), start_repair_request)],
            states={
                SELECTING_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_service_type)],
                DESCRIBING_PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, describe_problem)],
                ENTERING_CONTACTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_contacts)],
            },
            fallbacks=[MessageHandler(filters.Regex('^(🔙 Отмена)$'), cancel_repair)],
        )
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_cmd))
        app.add_handler(CommandHandler("contacts", contacts))
        app.add_handler(repair_handler)
        
        # Один главный обработчик для ВСЕХ текстовых сообщений
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # ЗАКОММЕНТИРОВАНО: Запуск фоновой задачи для напоминаний
        # (требует установки python-telegram-bot[job-queue])
        # app.job_queue.run_repeating(
        #     callback=lambda ctx: start_reminder_service(),
        #     interval=10,
        #     first=5
        # )
        
        print("✅ БОТ УСПЕШНО ЗАПУЩЕН!")
        print("📱 Откройте Telegram и напишите /start")
        print("🛑 Ctrl+C для остановки")
        print("=" * 50)
        
        app.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()