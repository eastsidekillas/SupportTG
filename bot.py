import telebot
from telebot import types
import config

bot = telebot.TeleBot(config.tokenbot)

user_dict = {}

class User:
    def __init__(self, name):
        self.name = name

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.from_user.id, "Привет, я бот техподдержки. Пожалуйста, отправь номер кабинета или имя:")

    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        msg = bot.send_message(message.from_user.id, 'Введи кабинет или имя: ')
        bot.register_next_step_handler(msg, report_message)

    except Exception as e:
        bot.reply_to(message, 'Ошибка')

def report_message(message):
    try:
        user_id = message.from_user.id
        user_info = user_dict[user_id]
        user_info.name = message.text

        msg = bot.send_message(user_id, 'Опишите вашу проблему:')
        user_info.msg = msg

        bot.register_next_step_handler(msg, get_problem_description)

    except Exception as e:
        bot.reply_to(message, 'Ошибка')

def get_problem_description(message):
    try:
        user_id = message.from_user.id
        user_info = user_dict[user_id]
        user_info.description = message.text

        msg = bot.send_message(user_id, 'Хорошо, теперь укажите ваш номер телефона:')
        user_info.msg = msg

        bot.register_next_step_handler(msg, report_to_group)

    except Exception as e:
        bot.reply_to(message, 'Ошибка')

def report_to_group(message):
    user_id = message.from_user.id
    user_info = user_dict[user_id]

    if user_info:
        try:
            report = user_info.name
            description = user_info.description
            contact_info = message.text
            user_name = message.from_user.username
            user_nick = message.from_user.first_name

            final_report = f"Кабинет: {report}\nОписание проблемы: {description}\nКонтактные данные: @{user_name} ({user_nick}), {contact_info}\n"

            bot.send_message(message.from_user.id, 'Ваше сообщение доставлено, специалист рассмотрит вашу проблему')
            bot.send_message(config.groupid, final_report)

            send_welcome(message)  # Возврат в главное меню

        except Exception as e:
            bot.send_message(config.groupid, f'Произошла ошибка: {e}')
    else:
        bot.send_message(message.from_user.id, 'Что-то пошло не так. Пожалуйста, отправьте информацию заново.')

bot.polling()
