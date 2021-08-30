from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from info import token_tg
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
        where UPPER(pharmacy.city) = UPPER('{city}')""").fetchall()
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


def phone_format(phone):
    try:
        if phone[0] == '8':
            phone = '+7' + phone[1:]
    except Exception:
        phone = '-'
    return phone


def cost_format(cost):
    r, k = cost.split(',')
    format_cost = r + ' руб ' + k[:2] + ' коп'
    return format_cost


def pharmacy_format(s):
    x = '-'
    return f"* {s[1]}\nЧасы работы: {s[3] if s[3] is not None else x}\nАдрес: {s[2]}\n" \
           f"Телефон: {phone_format(s[4])}\nСсылка на карты: " \
           f"https://maps.yandex.ru/?source=serp_navig&text={''.join(s[2].split())}\n"


def start(update, context):
    user = update.message.from_user.first_name
    update.message.reply_text(
        f"Здравствуйте, {user}! Какой препарат вам необходимо найти? Напишите его название кириллицей.")
    if 'log' not in context.user_data.keys():
        context.user_data['log'] = True
    if 'phase' not in context.user_data.keys():
        context.user_data['phase'] = 1
    return 1


def conv_handler(update, context):  # функция, руководящая основным диалогом
    if 'phase' not in context.user_data.keys():
        return start(update, context)
    if context.user_data['phase'] == 1:
        context.user_data['phase'] = name(update, context)
    elif context.user_data['phase'] == 2:
        context.user_data['phase'] = form(update, context)
    elif context.user_data['phase'] == 3:
        context.user_data['phase'] = dose(update, context)
    elif context.user_data['phase'] == 4:
        context.user_data['phase'] = control(update, context)
    elif context.user_data['phase'] == 5:
        context.user_data['phase'] = city(update, context)
    elif context.user_data['phase'] == 6:
        context.user_data['phase'] = dop_question(update, context)
    elif context.user_data['phase'] == 7:
        context.user_data['phase'] = dop_question_city(update, context)
    elif context.user_data['phase'] == 8:
        context.user_data['phase'] = other_city_or_repeat(update, context)


def name(update, context):  # обработка введенного текста как название препарата
    context.user_data['name'] = update.message.text
    result = medicine_ask(update.message.text)
    if context.user_data['log'] is False:
        result = list(filter(lambda x: x[1].lower() == context.user_data['name'].lower(), result))
        if result == []:
            update.message.reply_text(
                "К сожалению я не понимаю Вас. Выберите нужный препарат на высвечиваемой клавиатуре.")
            return 1
    if result == []:
        update.message.reply_text(
            'Извините, такого лекарства в моей базе нет, проверьте правильность написания. '
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
    reply_keyboard = [[el] for el in list(set([el[2] for el in result]))]
    update.message.reply_text("Выберите одну из известных нам форм выпуска:",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 2


def form(update, context):  # обработка введенного как форма выпуска
    context.user_data['log'] = True
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


def dose(update, context):  # обработка введенного как доза
    context.user_data['dose'] = update.message.text
    result = list(filter(lambda x: x[3] == context.user_data['dose'], context.user_data['result']))
    if result == []:
        update.message.reply_text('К сожалению я не понял Вас. Выберите дозировку еще раз.')
        return 3
    context.user_data['result'] = result
    s = f"Название: {result[0][1]}\nФорма выпуска: {result[0][2]}\nДозировка: {result[0][3]}"
    update.message.reply_text(f"Вы хотите найти информацию об этом препарате?\n\n{s}",
                              reply_markup=ReplyKeyboardMarkup(
                                  [['Да, все верно', 'Нет, начать сначала']],
                                  one_time_keyboard=True))
    return 4


def control(update, context):  # проверка на вывод инфы о препарате или о repeat
    text = update.message.text
    if text == 'Да, все верно':
        if 'fav_pharm' in context.user_data.keys() and context.user_data['fav_pharm'] is not None:
            result = data_ask((context.user_data['fav_pharm'][0], context.user_data['fav_pharm'][0]),
                              context.user_data['result'][0][4])
            if result != []:
                update.message.reply_text(
                    f"По запросу {context.user_data['result'][0][1]}, {context.user_data['result'][0][2]},"
                    f" {context.user_data['result'][0][3]} в вашей любимой аптеке\n"
                    f"{pharmacy_format(context.user_data['fav_pharm'])}"
                    f"Цена: {cost_format(result[0][1])}",
                    reply_markup=ReplyKeyboardRemove())
            else:
                update.message.reply_text(
                    "К сожалению в Вашей любимой аптеке нет интересующего Вас препарата.")
            update.message.reply_text("Хотите узнать о наличии препарата в других аптеках?",
                                      reply_markup=ReplyKeyboardMarkup(
                                          [['Нет, спасибо'], ['Да, в других аптеках моего города'],
                                           ['Да, в аптеках другого города']],
                                          one_time_keyboard=True))
            return 6
        if 'city' in context.user_data.keys():
            update.message.reply_text(
                f"Хотите узнать о наличии препарата в аптеках города {context.user_data['city'].capitalize()}?",
                reply_markup=ReplyKeyboardMarkup(
                    [['Да'],
                     ['Нет, в аптеках другого города']],
                    one_time_keyboard=True))
            return 7
        update.message.reply_text("Введите название Вашего города.", reply_markup=ReplyKeyboardRemove())
        return 5
    elif text == 'Нет, начать сначала':
        update.message.reply_text("Введите название интересующего Вас препарта кириллицей.",
                                  reply_markup=ReplyKeyboardRemove())
        context.user_data['log'] = True
        return 1
    else:
        update.message.reply_text("Так да или нет?",
                                  reply_markup=ReplyKeyboardMarkup(
                                      [['Да, все верно', 'Нет, начать сначала']],
                                      one_time_keyboard=True))
        return 4


def dop_question(update, context):  # обработка на выдачу инфы в других аптеках
    text = update.message.text
    if text == 'Нет, спасибо':
        update.message.reply_text(
            "Хорошо. Если Вас интересует еще какой-нибудь препарат, введите его название.",
            reply_markup=ReplyKeyboardRemove())
        context.user_data['log'] = True
        return 1
    elif text == 'Да, в других аптеках моего города':
        context.user_data['city'] = context.user_data['city']
        result = pharmacy_ask(context.user_data['city'])
        pharmacy_id = [el[0] for el in result]
        costs = data_ask(tuple(pharmacy_id), context.user_data['result'][0][4])
        answer = ''
        for el in costs:
            s = list(filter(lambda x: x[0] == el[0], result))
            s = f"{pharmacy_format(s[0])}" \
                f"Цена: {cost_format(el[1])}\n\n"
            answer += s
        update.message.reply_text(
            f"По запросу {context.user_data['result'][0][1]}, {context.user_data['result'][0][2]},"
            f" {context.user_data['result'][0][3]}:\n"
            f"\n{answer}", reply_markup=ReplyKeyboardRemove())
        update.message.reply_text(
            "Хотите узнать информацию о наличии препарата в аптеках других городов?",
            reply_markup=ReplyKeyboardMarkup(
                [['Да'], ['Нет, спасибо']],
                one_time_keyboard=True))
        return 8
    elif text == 'Да, в аптеках другого города':
        update.message.reply_text("Введите название интересующего Вас города.",
                                  reply_markup=ReplyKeyboardRemove())
        return 5
    update.message.reply_text("К сожалению я не понял Вас. Попробуйте еще раз",
                              reply_markup=ReplyKeyboardMarkup(
                                  [['Нет, спасибо'], ['Да, в других аптеках моего города'],
                                   ['Да, в аптеках другого города']],
                                  one_time_keyboard=True))
    return 6


def dop_question_city(update, context):  # выдавать ли инфу в других городах
    text = update.message.text
    if text == 'Да':
        result = pharmacy_ask(context.user_data['city'])
        pharmacy_id = [el[0] for el in result]
        costs = data_ask(tuple(pharmacy_id), context.user_data['result'][0][4])
        answer = ''
        for el in costs:
            s = list(filter(lambda x: x[0] == el[0], result))
            s = f"{pharmacy_format(s[0])}" \
                f"Цена: {cost_format(el[1])}\n\n"
            answer += s
        update.message.reply_text(
            f"По запросу {context.user_data['result'][0][1]}, {context.user_data['result'][0][2]},"
            f" {context.user_data['result'][0][3]}:\n"
            f"\n{answer}", reply_markup=ReplyKeyboardRemove())
        update.message.reply_text(
            "Хотите узнать информацию о наличии препарата в аптеках других городов?",
            reply_markup=ReplyKeyboardMarkup(
                [['Да'], ['Нет, спасибо']],
                one_time_keyboard=True))
        return 8
    elif text == 'Нет, в аптеках другого города':
        update.message.reply_text("Введите название интересующего Вас города.",
                                  reply_markup=ReplyKeyboardRemove())
        return 5
    update.message.reply_text("К сожалению я не понял Вас. Попробуйте еще раз")
    return 7


def city(update, context):  # выдать инфу по введенному названию города
    context.user_data['city'] = update.message.text
    result = pharmacy_ask(context.user_data['city'])
    if result == []:
        update.message.reply_text(
            f"Извините, такого города в моей базе нет, проверьте правильность написания. "
            f"Если всё верно, значит я с этим городом не работаю :(")
        return 5
    pharmacy_id = [el[0] for el in result]
    costs = data_ask(tuple(pharmacy_id), context.user_data['result'][0][4])
    answer = ''
    for el in costs:
        s = list(filter(lambda x: x[0] == el[0], result))
        s = f"{pharmacy_format(s[0])}" \
            f"Цена: {cost_format(el[1])}\n\n"
        answer += s
    update.message.reply_text(
        f"По запросу {context.user_data['result'][0][1]}, {context.user_data['result'][0][2]},"
        f" {context.user_data['result'][0][3]}:\n"
        f"\n{answer}", reply_markup=ReplyKeyboardRemove())
    update.message.reply_text("Хотите узнать информацию о наличии препарата в аптеках других городов?",
                              reply_markup=ReplyKeyboardMarkup(
                                  [['Да'], ['Нет, спасибо']],
                                  one_time_keyboard=True))
    return 8


def other_city_or_repeat(update, context):  # разрешение на начало нового цикла общения
    text = update.message.text
    if text == 'Да':
        update.message.reply_text("Введите название интересующего Вас города.",
                                  reply_markup=ReplyKeyboardRemove())
        return 5
    elif text == 'Нет, спасибо':
        update.message.reply_text(
            "Хорошо. Если Вас интересует еще какой-нибудь препарат, введите его название.",
            reply_markup=ReplyKeyboardRemove())
        context.user_data['log'] = True
        return 1
    update.message.reply_text("К сожалению я не понял Вас. Попробуйте еще раз")
    return 8


def pharmacy_start(update, context):
    user = update.message.from_user.first_name
    update.message.reply_text(
        f"Здравствуйте, {user}! Введите Ваш город. "
        "В любой момент можете ввести /stop для прекращения.")
    context.user_data['log'] = True
    return 1


def pharmacy_city(update, context):
    if update.message.text == '/stop':
        return stop(update, context)

    context.user_data['city'] = update.message.text
    result = pharmacy_ask(context.user_data['city'])
    if result == []:
        update.message.reply_text(
            f"Извините, такого города в моей базе нет, проверьте правильность написания. "
            f"Если всё верно, значит я с этим городом не работаю :(")
        return 1
    context.user_data['pharmacies'] = result
    pharmacies = '\n\n'.join(
        [str(i + 1) + '.  ' + result[i][1] + '\nАдрес: ' + result[i][2] for i in range(len(result))])
    buttons = [[str(i)] for i in range(len(result) + 1)]
    update.message.reply_text(
        f'Выберите подходящую вам аптеку:\n\n0. Мне ничего не подходит...\n\n{pharmacies}',
        reply_markup=ReplyKeyboardMarkup(buttons,
                                         one_time_keyboard=True))
    return 2


def pharmacy_choose(update, context):
    if update.message.text == '/stop':
        return stop(update, context)

    text = update.message.text
    if text == '0':
        return stop(update, context)
    try:
        context.user_data['fav_pharm'] = context.user_data['pharmacies'][int(text) - 1]
        update.message.reply_text('Я запомнил Ваш выбор!', reply_markup=ReplyKeyboardRemove())
    except Exception:
        update.message.reply_text("К сожалению я не понял Вас. Попробуйте снова")
        return 2
    return ConversationHandler.END


def stop(update, context):
    update.message.reply_text("Всего доброго", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def pharmacy_del(update, context):
    context.user_data['fav_pharm'] = None
    update.message.reply_text("Ваша любимая аптека удалена")


def pharmacy_view(update, context):
    x = '-'
    if 'fav_pharm' not in context.user_data.keys() or context.user_data['fav_pharm'] is None:
        update.message.reply_text(f"Вы не выбрали Вашу любимую аптеку...")
    else:
        update.message.reply_text(f"Ваша любимая аптека:\n\n"
                                  f"{pharmacy_format(context.user_data['fav_pharm'])}")


def help(update, context):
    update.message.reply_text(
        "Введите название лекарства, правильно ответьте на вопросы бота и узнайте, "
        "где можно купить интересующий Вас препарат.\nНа данный момент я знаю только лекарства, "
        "предназначенные для лечения заболевания респираторной системы (по классификации АТХ).\n"
        "Введите /set_favourite_pharmacy и выберите фаворитную аптеку. "
        "Бот будет выводить информацию по лекарствам прежде всего по этой аптеке.\n"
        "Введите /delete_favourite_pharmacy чтобы удалить любимую аптеку.\n"
        "Введите /view_favourite_pharmacy чтобы увидеть Вашу любимую аптеку.\n\n"
        "'Тут должно быть что-то умное и полезное'\n© подвал нашего сайта\n\n"
        "Коган Анна: Разработчик █████;\nМатевосян Артем: разработчик [ДАННЫЕ УДАЛЕНЫ].")


def main_tg():
    updater = Updater(token_tg, use_context=True, )
    dp = updater.dispatcher
    pharmacy_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('set_favourite_pharmacy', pharmacy_start)],

        states={
            1: [MessageHandler(Filters.text, pharmacy_city, pass_user_data=True)],
            2: [MessageHandler(Filters.text, pharmacy_choose, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(pharmacy_conv_handler)
    dp.add_handler(CommandHandler("delete_favourite_pharmacy", pharmacy_del, pass_user_data=True))
    dp.add_handler(CommandHandler("view_favourite_pharmacy", pharmacy_view, pass_user_data=True))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start, pass_user_data=True))
    text_handler = MessageHandler(Filters.text, conv_handler, pass_user_data=True)
    dp.add_handler(text_handler)
    updater.start_polling()
    print('Бот начал свою работу......')
    updater.idle()


if __name__ == '__main__':
    main_tg()

# 1 - name()
# 2 - form()
# 3 - dose()
# 4 - control()
# 5 - city()
# 6 - dop_question()
# 7 - dop_question_city()
# 8 - other_city_or_repeat()
