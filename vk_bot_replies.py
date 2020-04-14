import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
import random


class VkBotReplies:
    """Этот класс содержит методы, отвечающие за, как иронично, ответы бота."""
    def __init__(self, bot_token, bot_id):
        self.id = bot_id
        self.token = bot_token
        self.vk_session = vk_api.VkApi(token=bot_token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, bot_id)

    def start(self, send_to):    # Первое сообщение, приветствие и вопрос о лекарстве
        username = self.vk.users.get(user_ids=send_to)['response']['first_name']
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message=f'Здравствуйте, {username}! Какой препарат вам необходимо найти?')

    def ask_for_location(self, send_to):    # Запрос местоположения или запрос города - зависит от выбора пользователя
        keyboard = '''{
            "one_time": true,
            "buttons": [
                [{
                    "action": {
                        "type": "location",
                        "payload": "{\\"button\\": \\"1\\"}"
                    }
                }],
                [
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\\"button\\": \\"2\\"}",
                            "label": "Указать город"
                        },
                        "color": "primary"
                    }
                ]
            ]
        }'''
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message='Укажите свой город или отправьте местоположение, '
                                      'чтобы я нашёл ближайшие аптеки.',
                              keyboard=keyboard)

    def ask_city(self, send_to):    # Вызывается при недоступности клавиатуры бота или по выбору пользователя
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message='Укажите свой город, '
                                      'чтобы я нашёл ближайшие аптеки.')
