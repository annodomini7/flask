import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_bot_replies import VkBotReplies
import requests
import time
import sqlite3
import re


VK_BOT_ID = 000000000
VK_BOT_TOKEN = 'token'


def sqlite_like(template_, value_):
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


class User:    # Класс, экземпляры которого будут хранить информацию о пользователе и его текущем поиске
    def __init__(self, user_id):
        self.user_id = user_id
        self.status = None
        self.req_medicine = None
        self.med_form = None
        self.dose = None
        self.city = None


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
                # пользователь только начал диалог?
                if users.get(user_id, None) is None:
                    users[user_id] = User(user_id)
                    bot.start(user_id)
                    users[user_id].status = 'waiting_for_medicine'
                # пользователь отправил название медикамента?
                elif users[user_id].status == 'waiting_for_medicine':
                    db_request_result = cur.execute(f'''SELECT DISTINCT name FROM medicine
                                                        WHERE LOWER(medicine.name) LIKE
                                                        LOWER('%{msg['text']}%')''').fetchall()
                    if not db_request_result:
                        bot.return_msg(user_id, 'Извините, не удалось найти данный препарат в базе данных. '
                                                'Проверьте написание и попробуйте ещё раз.')
                    else:
                        users[user_id].req_medicine = tuple(map(lambda x: x[0], db_request_result))
                        if len(users[user_id].req_medicine) > 10:
                            bot.return_msg(user_id, 'Запрос слишком неточный, сделайте его немного длиннее!')
                            users[user_id] = User(user_id)
                            users[user_id].status = 'waiting_for_medicine'
                        elif len(users[user_id].req_medicine) > 1:
                            bot.clarify_name(user_id, users[user_id].req_medicine)
                            users[user_id].status = 'waiting_for_clarification'
                        else:
                            bot.ask_for_location(user_id, users[user_id].req_medicine[0])
                            users[user_id].status = 'waiting_for_location'
                elif users[user_id].status == 'waiting_for_clarification':
                    clarification = cur.execute(f'''SELECT DISTINCT name FROM medicine
                    WHERE name = "{msg['text']}"''').fetchone()
                    if clarification is None:
                        bot.return_msg(user_id, 'Извините, не удалось найти данный препарат в базе данных. '
                                                'Попробуйте ещё раз, выберите одно из названий на клавиатуре.')
                        bot.clarify_name(user_id, users[user_id].req_medicine)
                    else:
                        users[user_id].req_medicine = clarification[0]
                        bot.ask_for_location(user_id, users[user_id].req_medicine)
                        users[user_id].status = 'waiting_for_location'
                # пользователь нажал "Указать город"?
                elif users[user_id].status == 'waiting_for_location' and 'указать город' in msg['text'].lower():
                    bot.ask_city(user_id)
                    users[user_id].status = 'waiting_for_city'
                elif ((users[user_id].status == 'waiting_for_location' and
                       'изменить выбор препарата' in msg['text'].lower())):
                    bot.return_msg(user_id, 'Выбор препарата сброшен. Теперь Вы можете указать его заново.')
                    users[user_id] = User(user_id)
                    users[user_id].status = 'waiting_for_medicine'
                # пользователь указал сам город?
                elif users[user_id].status == 'waiting_for_city':
                    users[user_id].city = msg['text']
                    bot.send_results(user_id, users[user_id].__dict__)
                    del users[user_id]
            except Exception as e:
                bot.return_msg(user_id, e)
                if not users.get(user_id, None) is None:
                    del users[user_id]


if __name__ == '__main__':
    while True:
        try:
            message_handler(VK_BOT_TOKEN, VK_BOT_ID)
        except requests.exceptions.ReadTimeout:
            time.sleep(3)
