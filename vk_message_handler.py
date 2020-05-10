import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_bot_replies import VkBotReplies
import requests
import time
import sqlite3
import re


def sqlite_like(template_, value_):    # До следующего комментария идут функции для решения проблем поиска в БД
    return sqlite_like_escape(template_, value_, None)


def sqlite_like_escape(template_, value_, escape_):
    re_ = re.compile(template_.lower().replace(".", "\\.").replace("^", "\\^")
                     .replace("$", "\\$").replace("*", "\\*").replace("+", "\\+")
                     .replace("?", "\\?").replace("{", "\\{").replace("}", "\\}")
                     .replace("(", "\\(").replace(")", "\\)").replace("[", "\\[")
                     .replace("]", "\\]").replace("_", ".").replace("%", ".*?"))
    return re_.match(value_.lower()) is not None


def sqlite_lower(value_):
    return value_.lower()


def sqlite_upper(value_):
    return value_.upper()


def sqlite_nocase_collation(value1_, value2_):
    return (value1_.encode('utf-8').lower() < value2_.encode('utf-8').lower()) -\
           (value1_.encode('utf-8').lower() > value2_.encode('utf-8').lower())


def find_stores(cursor, city, barcode):    # Поиск конкретного лекарства в аптеках по его коду и городу
    barcode_stores = cursor.execute(f'''SELECT pharmacy_id, cost FROM data WHERE barcode = {barcode}''').fetchall()
    barcode_stores_ids = tuple(map(lambda x: x[0], barcode_stores))
    barcode_stores = {x[0]: x[1] for x in barcode_stores}
    city_stores = cursor.execute(f'''SELECT id, name, address, hours, phone FROM pharmacy
                                     WHERE city = "{city}" AND id in {barcode_stores_ids}''').fetchall()
    return tuple(tuple(list(x) + [barcode_stores[x[0]]]) for x in city_stores)


def medicine_search(cursor, name):
    request_result = cursor.execute(f'''SELECT DISTINCT name FROM medicine
                                        WHERE LOWER(medicine.name) LIKE
                                        LOWER('%{name}%')''').fetchall()
    if not request_result:
        return None
    return tuple(map(lambda x: x[0], request_result))


def form_search(cursor, name):
    request_result = cursor.execute(f'''SELECT DISTINCT form FROM medicine
                                        WHERE name = "{name}"''').fetchall()
    if not request_result:
        return None
    return tuple(map(lambda x: x[0], request_result))


def dose_search(cursor, name, form):
    request_result = cursor.execute(f'''SELECT DISTINCT form, dose FROM medicine
    WHERE name = "{name}" and form = "{form}"''').fetchall()
    if request_result:
        return request_result[0][0], tuple(map(lambda x: x[1], request_result))
    return None


class User:    # Класс, экземпляры которого будут хранить информацию о пользователе и его текущем поиске
    def __init__(self, user_id):
        self.user_id = user_id
        self.status = None
        self.req_medicine = None
        self.med_form = None
        self.dose = None
        self.city = None
        self.barcode = None


def message_handler(token, vk_id):
    users = dict()    # в этом словаре будут храниться экземпляры класса User, ключами будут ID

    vk_session = vk_api.VkApi(token=token)
    bot = VkBotReplies(vk_session)
    longpoll = VkBotLongPoll(vk_session, vk_id)

    con = sqlite3.connect('db/pharmacy.db')
    con.create_collation("BINARY", sqlite_nocase_collation)
    con.create_collation("NOCASE", sqlite_nocase_collation)
    con.create_function("LIKE", 2, sqlite_like)
    con.create_function("LOWER", 1, sqlite_lower)
    con.create_function("UPPER", 1, sqlite_upper)
    cur = con.cursor()

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.object.message['from_id']
            msg = event.object.message
            try:
                # пользователю нужна справка?
                if msg['text'].lower() == 'помощь':
                    bot.help(user_id)
                # Пасхалка!
                elif msg['text'].lower() == 'галоперидол':
                    bot.return_msg(user_id, 'А ну в палату! Колоть будем по расписанию!')
                # пользователь только начал диалог?
                elif users.get(user_id, None) is None:
                    users[user_id] = User(user_id)
                    bot.start(user_id)
                    users[user_id].status = 'waiting_for_medicine'
                # пользователь отправил название медикамента?
                elif users[user_id].status == 'waiting_for_medicine':
                    found = medicine_search(cur, msg['text'])
                    if not found:
                        bot.return_msg(user_id, 'Извините, не удалось найти данный препарат в базе данных. '
                                                'Проверьте написание и попробуйте ещё раз.')
                    elif len(found) > 10:
                        bot.return_msg(user_id, 'Запрос слишком неточный, сделайте его немного длиннее!')
                    else:
                        users[user_id].req_medicine = found
                        bot.clarify_name(user_id, found)
                        users[user_id].status = 'waiting_for_clarification'
                # пользователь выбрал препарат из списка?
                elif users[user_id].status == 'waiting_for_clarification':
                    clarification = cur.execute(f'''SELECT DISTINCT name FROM medicine
                    WHERE name = "{msg['text']}"''').fetchone()
                    if not clarification:
                        bot.return_msg(user_id, 'Извините, я вас не понимаю. '
                                                'Попробуйте ещё раз, выбрав одно из названий на клавиатуре.')
                        bot.clarify_name(user_id, users[user_id].req_medicine)
                    else:
                        users[user_id].req_medicine = clarification[0]
                        users[user_id].med_form = form_search(cur, users[user_id].req_medicine)
                        bot.ask_med_form(user_id, users[user_id].med_form)
                        users[user_id].status = 'waiting_for_med_form'
                # пользователь указал форму выпуска?
                elif users[user_id].status == 'waiting_for_med_form':
                    found = dose_search(cur, users[user_id].req_medicine, msg['text'])
                    if found:
                        users[user_id].med_form, users[user_id].dose = found
                        bot.ask_dose(user_id, users[user_id].dose)
                        users[user_id].status = 'waiting_for_dose'
                    else:
                        bot.ask_med_form(user_id, users[user_id].med_form)
                # пользователь указал дозировку?
                elif users[user_id].status == 'waiting_for_dose':
                    found = cur.execute(f'''SELECT DISTINCT dose FROM medicine
                                        WHERE name = "{users[user_id].req_medicine}" and
                                        form = "{users[user_id].med_form}" and dose = "{msg['text']}"''').fetchone()
                    if found:
                        users[user_id].dose = found[0]
                        users[user_id].status = 'waiting_for_location'
                        bot.location_or_cancel(user_id, users[user_id])
                    else:
                        bot.ask_dose(user_id, users[user_id].dose)
                # пользователь подтвердил выбор препарата?
                elif users[user_id].status == 'waiting_for_location' and 'указать город' in msg['text'].lower():
                    bot.ask_city(user_id)
                    users[user_id].status = 'waiting_for_city'
                # пользователь отменил выбор препарата?
                elif ((users[user_id].status == 'waiting_for_location' and
                       'изменить выбор препарата' in msg['text'].lower())):
                    bot.return_msg(user_id, 'Выбор препарата сброшен. Теперь Вы можете указать его заново.')
                    users[user_id] = User(user_id)
                    users[user_id].status = 'waiting_for_medicine'
                # "Так да или нет?"
                elif users[user_id].status == 'waiting_for_location':
                    bot.location_or_cancel(user_id, users[user_id])
                # пользователь указал сам город?
                elif users[user_id].status == 'waiting_for_city':
                    db_request_result = cur.execute(f'''SELECT DISTINCT city FROM pharmacy
                                                        WHERE LOWER(pharmacy.city) =
                                                        LOWER('{msg['text']}')''').fetchone()
                    if db_request_result:
                        users[user_id].city = db_request_result[0]
                        users[user_id].barcode = cur.execute(f'''SELECT DISTINCT barcode FROM medicine
                        WHERE name = '{users[user_id].req_medicine}' and form = '{users[user_id].med_form}'
                        and dose = "{users[user_id].dose}"''').fetchone()[0]
                        bot.send_results(user_id, find_stores(cur, users[user_id].city, users[user_id].barcode))
                    else:
                        bot.return_msg(user_id, 'Я не знаю такой город, проверьте написание! '
                                                'Если вы уверены, что написано верно, значит, '
                                                'я с этим городом пока что не работаю :(')
                    bot.shall_i_try_again(user_id)
                    users[user_id].status = 'waiting_for_again_decision'
                # пользователь решил поискать в другом городе?
                elif ((users[user_id].status == 'waiting_for_again_decision' and
                       msg['text'].lower() == 'посмотреть в другом городе')):
                    bot.ask_city(user_id)
                    users[user_id].status = 'waiting_for_city'
                # пользователь решил больше ничего не искать?
                elif ((users[user_id].status == 'waiting_for_again_decision' and
                       msg['text'].lower() == 'больше не нужно')):
                    bot.return_msg(user_id, 'Всего доброго!')
                    del users[user_id]
                # "Так вы будете искать в другом городе или нет?"
                elif users[user_id].status == 'waiting_for_again_decision':
                    bot.shall_i_try_again(user_id)
            except Exception as e:
                bot.return_msg(user_id, e)
                if not users.get(user_id, None) is None:
                    del users[user_id]


def main_vk():
    vk_bot_id = 194193564
    vk_bot_token = '323c38229e86b2ad629e1dda5ae6ef7c0f97d3c304677984c57d889f737f8b1d08b62a7851a510895ab8c'
    while True:
        try:
            message_handler(vk_bot_token, vk_bot_id)
        except requests.exceptions.ReadTimeout:
            time.sleep(3)


if __name__ == '__main__':
    main_vk()
