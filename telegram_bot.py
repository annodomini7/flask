from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, PhotoSize
from telegram import ReplyKeyboardRemove
from random import randint
import requests
import sqlite3
import re


def sqlite_like(template_, value_):
    return sqlite_like_escape(template_, value_, None)


def sqlite_like_escape(template_, value_, escape_):
    re_ = re.compile(template_.lower().
                     replace(".", "\\.").replace("^", "\\^").replace("$", "\\$").
                     replace("*", "\\*").replace("+", "\\+").replace("?", "\\?").
                     replace("{", "\\{").replace("}", "\\}").replace("(", "\\(").
                     replace(")", "\\)").replace("[", "\\[").replace("]", "\\]").
                     replace("_", ".").replace("%", ".*?"))
    return re_.match(value_.lower()) is not None


def sqlite_lower(value_):
    return value_.lower()


def sqlite_upper(value_):
    return value_.upper()


def sqlite_nocase_collation(value1_, value2_):
    return (value1_.encode('utf-8').lower() < value2_.encode('utf-8').lower()) - (
            value1_.encode('utf-8').lower() > value2_.encode('utf-8').lower())


def work(name):
    con = sqlite3.connect("db/pharmacy.db")
    con.create_collation("BINARY", sqlite_nocase_collation)
    con.create_collation("NOCASE", sqlite_nocase_collation)
    con.create_function("LIKE", 2, sqlite_like)
    con.create_function("UPPER", 1, sqlite_upper)
    cur = con.cursor()
    print(name)
    result = cur.execute(
        f"""select *
        from medicine
        where UPPER(medicine.name) LIKE UPPER('%{name}%')""").fetchall()
    print(result)
    return result


#  print(work('лазолван'))


def start(update, context):
    update.message.reply_text(
        "Здравствуйте! Какой препарат вам необходимо найти? Напишите его название с заглавной буквы кириллицей.")
    return 1


def name(update, context):
    context.user_data['name'] = update.message.text
    print(update.message.text)
    result = work(update.message.text)
    context.user_data['result'] = result
    if result == []:
        update.message.reply_text('К сожалению такого лекарства нет в нашей базе. Попробуйте ввести другое название.')
        return 1
    form = '\n'.join(list(set([el[2] for el in result])))
    update.message.reply_text(f"Выберите одну из известных нам форм выпуска и введите ее название: \n{form}")
    return 2


def form(update, context):
    context.user_data['form'] = update.message.text.lower()
    result = list(filter(lambda x: x[2] == context.user_data['form'], context.user_data['result']))
    context.user_data['result'] = result
    if result == []:
        update.message.reply_text('incorrect form')
        return 2
    dose = '\n'.join(list(set([el[3] for el in result])))
    update.message.reply_text(f"Выберите одну из известных нам доз и введите ее название: \n{dose}")
    return 3


def dose(update, context):
    context.user_data['dose'] = update.message.text
    result = list(filter(lambda x: x[3] == context.user_data['dose'], context.user_data['result']))
    context.user_data['result'] = result
    if result == []:
        update.message.reply_text('incorrect dose')
        return 3
    print(result)
    update.message.reply_text(f"Введите ваш город")
    return 4


def city(update, context):
    context.user_data['city'] = update.message.text
    update.message.reply_text(f"{context.user_data['city']}")
    return ConversationHandler.END


def stop(update, context):
    return ConversationHandler.END


def main():
    REQUEST_KWARGS = {
        'proxy_url': 'socks5://85.10.235.14:1080', }

    updater = Updater("925371295:AAGqnKomvyfxqJmpqMppZ2ttO3zf0VUM818", use_context=True,
                      request_kwargs=REQUEST_KWARGS)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            1: [MessageHandler(Filters.text, name, pass_user_data=True)],
            2: [MessageHandler(Filters.text, form, pass_user_data=True)],
            3: [MessageHandler(Filters.text, dose, pass_user_data=True)],
            4: [MessageHandler(Filters.text, city, pass_user_data=True)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    print('Бот начал свою работу......')
    updater.idle()


if __name__ == '__main__':
    main()
