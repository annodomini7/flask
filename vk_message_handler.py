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


def database_search(cursor, entity, **info):
    request = f'SELECT * FROM {entity}'
    if info:
        request += '\nWHERE '
        request += ' AND '.join(f'{key} = "{value}"' for key, value in info.items())
    try:
        return cursor.execute(request).fetchall()
    except sqlite3.OperationalError:
        return None


def message_handler(token, vk_id):
    users = dict()
    users_info = dict()

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
            try:    # пользователь только начал диалог?
                if users.get(user_id, 'not_started') == 'not_started':
                    users_info[user_id] = dict()
                    bot.start(user_id)
                    users[user_id] = 'waiting_for_medicine'
                # пользователь отправил название медикамента?
                elif users[user_id] == 'waiting_for_medicine':
                    if database_search(cur, 'medicine', name=msg['text']):
                        users_info[user_id]['req_medicine'] = msg['text']
                        if (('location' in event.obj.client_info['button_actions'] and
                             'text' in event.obj.client_info['button_actions'])):
                            bot.ask_for_location(user_id)
                            users[user_id] = 'waiting_for_location'
                        else:
                            bot.ask_city(user_id)
                            users[user_id] = 'waiting_for_city'
                    else:
                        bot.return_msg(user_id, 'Извините, не удалось найти данный препарат в базе данных. '
                                                'Укажите его ещё раз.')
                # пользователь отправил местоположение?
                elif users[user_id] == 'waiting_for_location' and 'location' in msg['payload']:
                    users_info[user_id]['geo'] = msg['geo']
                    del users[user_id]
                    bot.send_results(user_id, users_info[user_id])
                    del users_info[user_id]
                # пользователь нажал "Указать город"?
                elif users[user_id] == 'waiting_for_location' and 'указать город' in msg['text'].lower():
                    bot.ask_city(user_id)
                    users[user_id] = 'waiting_for_city'
                # пользователь указал сам город?
                elif users[user_id] == 'waiting_for_city':
                    users_info[user_id]['city'] = msg['text']
                    del users[user_id]
                    bot.send_results(user_id, users_info[user_id])
                    del users_info[user_id]
            except Exception as e:
                bot.return_msg(user_id, e)
                if not users.get(user_id, None) is None:
                    del users[user_id]
                if not users_info.get(user_id, None) is None:
                    del users_info[user_id]


if __name__ == '__main__':
    while True:
        try:
            message_handler(VK_BOT_TOKEN, VK_BOT_ID)
        except requests.exceptions.ReadTimeout:
            time.sleep(3)
