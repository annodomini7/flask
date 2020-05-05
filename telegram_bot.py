from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
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


def medicine_ask(name):
    con = sqlite3.connect("db/pharmacy.db")
    con.create_collation("BINARY", sqlite_nocase_collation)
    con.create_collation("NOCASE", sqlite_nocase_collation)
    con.create_function("LIKE", 2, sqlite_like)
    con.create_function("UPPER", 1, sqlite_upper)
    cur = con.cursor()
    result = cur.execute(
        f"""select *
        from medicine
        where UPPER(medicine.name) LIKE UPPER('%{name}%')""").fetchall()
    return result


def pharmacy_ask(city):
    con = sqlite3.connect("db/pharmacy.db")
    con.create_collation("BINARY", sqlite_nocase_collation)
    con.create_collation("NOCASE", sqlite_nocase_collation)
    con.create_function("LIKE", 2, sqlite_like)
    con.create_function("UPPER", 1, sqlite_upper)
    cur = con.cursor()
    result = cur.execute(
        f"""select id, name, address, hours, phone
        from pharmacy
        where UPPER(pharmacy.city) LIKE UPPER('%{city}%')""").fetchall()
    return result


def data_ask(pharmacy_id, barcode):
    con = sqlite3.connect("db/pharmacy.db")
    con.create_collation("BINARY", sqlite_nocase_collation)
    con.create_collation("NOCASE", sqlite_nocase_collation)
    con.create_function("LIKE", 2, sqlite_like)
    con.create_function("UPPER", 1, sqlite_upper)
    cur = con.cursor()
    result = cur.execute(
        f"""select pharmacy_id, cost
            from data
            where data.barcode = {barcode}
            and data.pharmacy_id in {pharmacy_id}""").fetchall()
    return list(set(result))


def start(update, context):
    user = update.message.from_user.first_name
    update.message.reply_text(
        f"Здравствуйте, {user}! Какой препарат вам необходимо найти? Напишите его название кириллицей. "
        "В любой момент можете ввести /stop для прекращения опроса.")
    context.user_data['log'] = True
    return 1


def name(update, context):
    if update.message.text == '/stop':
        update.message.reply_text("Всего доброго", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    context.user_data['name'] = update.message.text
    result = medicine_ask(update.message.text)
    if context.user_data['log'] is False:
        result = list(filter(lambda x: x[1].lower() == context.user_data['name'].lower(), result))
        if result == []:
            update.message.reply_text(
                "К сожалению я не понимаю Вас. Выберите нужный препарат на высвечиваемой клавиатуре.")
            return 1
    if result == []:
        update.message.reply_text('Извините, такого лекарства в моей базе нет, проверьте правильность написания. '
                                  'Если всё верно, значит я с этим препаратом не работаю :(')
        return 1
    names = set([el[1] for el in result])
    if len(names) > 1:
        context.user_data['log'] = False
        reply_keyboard = [[el] for el in names]
        update.message.reply_text(
            "В нашей базе есть несколько препаратов с подходящими названиями. Выберите нужный Вам:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return 1
    if result[0][1].lower() != update.message.text.lower():
        reply_keyboard = [[el] for el in names]
        update.message.reply_text(
            "Вы имели в виду этот препарат?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return 1
    context.user_data['result'] = result
    print(result)
    reply_keyboard = [[el] for el in list(set([el[2] for el in result]))]
    update.message.reply_text("Выберите одну из известных нам форм выпуска:",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 2


def form(update, context):
    if update.message.text == '/stop':
        update.message.reply_text("Всего доброго", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    context.user_data['form'] = update.message.text.lower()
    result = list(filter(lambda x: x[2] == context.user_data['form'], context.user_data['result']))
    if result == []:
        update.message.reply_text(
            'Нажмите клавишу на появившейся клавиатуре и выберите необходимую форму выпуска товара.')
        return 2
    context.user_data['result'] = result
    reply_keyboard = [[el] for el in list(set([el[3] for el in result]))]
    update.message.reply_text(f"Выберите одну из известных нам дозировок:",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 3


def dose(update, context):
    if update.message.text == '/stop':
        update.message.reply_text("Всего доброго", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    context.user_data['dose'] = update.message.text
    result = list(filter(lambda x: x[3] == context.user_data['dose'], context.user_data['result']))
    if result == []:
        update.message.reply_text('incorrect dose')
        return 3
    context.user_data['result'] = result
    s = f"Название: {result[0][1]};\nФорма выпуска: {result[0][2]};\nДозировка: {result[0][3]}"
    update.message.reply_text(f"Вы хотите найти информацию об этом препарате?\n\n{s}",
                              reply_markup=ReplyKeyboardMarkup([['Да, все верно', 'Нет, начать сначала']],
                                                               one_time_keyboard=True))
    return 4


def control(update, context):
    if update.message.text == '/stop':
        update.message.reply_text("Всего доброго", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    text = update.message.text
    if text == 'Да, все верно':
        update.message.reply_text("Введите название Вашего города.", reply_markup=ReplyKeyboardRemove())
        return 5
    elif text == 'Нет, начать сначала':
        update.message.reply_text("Введите название интересующего Вас препарта кириллицей.",
                                  reply_markup=ReplyKeyboardRemove())
        return 1
    else:
        update.message.reply_text("Так да или нет?",
                                  reply_markup=ReplyKeyboardMarkup([['Да, все верно', 'Нет, начать сначала']],
                                                                   one_time_keyboard=True))
        return 4


def city(update, context):
    if update.message.text == '/stop':
        update.message.reply_text("Всего доброго", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    context.user_data['city'] = update.message.text
    result = pharmacy_ask(context.user_data['city'])
    if result == []:
        update.message.reply_text(f"Извините, такого города в моей базе нет, проверьте правильность написания. "
                                  f"Если всё верно, значит я с этим городом не работаю :(")
        return 5
    pharmacy_id = [el[0] for el in result]
    costs = data_ask(tuple(pharmacy_id), context.user_data['result'][0][4])
    answer = ''
    for el in costs:
        s = list(filter(lambda x: x[0] == el[0], result))
        s = f"* {s[0][1]}\nЧасы работы: {s[0][3]}\nАдрес: {s[0][2]}\nТелефон: {s[0][4]}\nЦена: {el[1]}\n\n"
        answer += s
    update.message.reply_text(
        f"По запросу {context.user_data['result'][0][1]}, {context.user_data['result'][0][2]},"
        f" {context.user_data['result'][0][3]}:\n"
        f"\n{answer}")
    return ConversationHandler.END


def stop(update, context):
    update.message.reply_text("Всего доброго", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    REQUEST_KWARGS = {
        'proxy_url': 'socks5://85.10.235.14:1080', }

    updater = Updater("925371295:AAGqnKomvyfxqJmpqMppZ2ttO3zf0VUM818", use_context=True,
                      request_kwargs=REQUEST_KWARGS)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            1: [MessageHandler(Filters.text, name, pass_user_data=True)],
            2: [MessageHandler(Filters.text, form, pass_user_data=True)],
            3: [MessageHandler(Filters.text, dose, pass_user_data=True)],
            4: [MessageHandler(Filters.text, control, pass_user_data=True)],
            5: [MessageHandler(Filters.text, city, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    print('Бот начал свою работу......')
    updater.idle()


if __name__ == '__main__':
    main()
