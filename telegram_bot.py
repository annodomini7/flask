# Импортируем необходимые классы.
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, PhotoSize
from telegram import ReplyKeyboardRemove
from random import randint
import requests


def start(update, context):
    update.message.reply_text(
        "Input drug's name")
    return 1


def name(update, context):
    context.user_data['name'] = update.message.text
    update.message.reply_text(
        "Choose and input form")
    return 2


def form(update, context):
    context.user_data['form'] = update.message.text
    update.message.reply_text(
        "Choose and input dose")
    return 3


def dose(update, context):
    context.user_data['dose'] = update.message.text
    update.message.reply_text(
        "Choose and input city")
    return 4


def city(update, context):
    context.user_data['city'] = update.message.text
    update.message.reply_text(f"{context.user_data}")
    return ConversationHandler.END


def stop(update, context):
    return ConversationHandler.END


def main():
    REQUEST_KWARGS = {
        'proxy_url': 'socks5://97.74.230.16:31178', }

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
