from telegram.ext import CommandHandler
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram.ext import ConversationHandler


class TG_Replies:
    def __init__(self, updater):
        self.dp = updater.dispatcher
        self.information = {}
        self.conv_handler = ConversationHandler(
            # Точка входа в диалог.
            # В данном случае — команда /start. Она задаёт первый вопрос.
                entry_points=[CommandHandler('start', self.start)],

            # Состояние внутри диалога.
            # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
                states={
                # Функция читает ответ на первый вопрос и задаёт второй.
                    1: [MessageHandler(Filters.text, self.location)],
                # Функция читает ответ на второй вопрос и завершает диалог.
                    2: [MessageHandler(Filters.text, self.send_rezults)]
                },

            # Точка прерывания диалога. В данном случае — команда /stop.
                fallbacks=[CommandHandler('stop', self.stop)]
        )
        self.dp.add_handler(self.conv_handler)

    def start(self, update, context):
        update.message.reply_text(
        "Привет. Пройдите небольшой опрос, пожалуйста!\n"
        "Вы можете прервать опрос, послав команду /stop.\n"
        "В каком городе вы живёте?")
        return 1

    def location(self, update, context):
        # Это ответ на первый вопрос.
        # Мы можем использовать его во втором вопросе.
        self.information['medecine'] = update.message.text
        update.message.reply_text(
            "Какая погода в городе {locality}?".format(**locals()))
        # Следующее текстовое сообщение будет обработано
        # обработчиком states[2]
        return 2

    def send_rezults(self, update, context):
        update.message.reply_text(''.join([x for x in self.information.items()]))

    def stop(self, update, context):
        self.information = {}
        update.message.reply_text(
            "Какая погода в городе {locality}?".format(**locals()))



def main():
    updater = Updater(TOKEN, use_context=True)
    the_bot = TG_Replies()
    updater.start_polling()

    # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()