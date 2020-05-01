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
        self.geo = None
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
                    try:
                        users[user_id].req_medicine = cur.execute(f'''SELECT DISTINCT name FROM medicine
                        WHERE LOWER(medicine.name) LIKE LOWER('%{msg['text']}%')''').fetchall()
                    except sqlite3.OperationalError:
                        bot.return_msg(user_id, 'Извините, не удалось найти данный препарат в базе данных. '
                                                'Проверьте написание и попробуйте ещё раз.')
                    else:
                        if len(users[user_id].req_medicine) > 1:
                            bot.clarify_name(user_id, users[user_id].req_medicine)
                            users[user_id].status = 'waiting_for_clarification'
                        elif (('location' in event.obj.client_info['button_actions'] and
                             'text' in event.obj.client_info['button_actions'])):
                            bot.ask_for_location(user_id)
                            users[user_id].status = 'waiting_for_location'
                        else:
                            bot.ask_city(user_id)
                            users[user_id].status = 'waiting_for_city'
                elif users[user_id].status == 'waiting_for_clarification':
                    try:
                        clarification = cur.execute(f'''SELECT DISTINCT name FROM medicine
                        WHERE name = "{msg['text']}"''').fetchone()
                    except sqlite3.OperationalError:
                        bot.return_msg(user_id, 'Извините, не удалось найти данный препарат в базе данных. '
                                                'Попробуйте ещё раз, выберите одно из названий на клавиатуре.')
                        bot.clarify_name(user_id, users[user_id].req_medicine)
                    else:
                        users[user_id].req_medicine = clarification
                        if (('location' in event.obj.client_info['button_actions'] and
                             'text' in event.obj.client_info['button_actions'])):
                            bot.ask_for_location(user_id)
                            users[user_id].status = 'waiting_for_location'
                        else:
                            bot.ask_city(user_id)
                            users[user_id].status = 'waiting_for_city'
                # пользователь отправил местоположение?
                elif users[user_id].status == 'waiting_for_location' and 'location' in msg['payload']:
                    users[user_id].geo = msg['geo']
                    bot.send_results(user_id, users[user_id])
                    del users[user_id]
                # пользователь нажал "Указать город"?
                elif users[user_id].status == 'waiting_for_location' and 'указать город' in msg['text'].lower():
                    bot.ask_city(user_id)
                    users[user_id].status = 'waiting_for_city'
                # пользователь указал сам город?
                elif users[user_id].status == 'waiting_for_city':
                    users[user_id].city = msg['text']
                    bot.send_results(user_id, users[user_id])
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
