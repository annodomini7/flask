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

    def start(self, send_to):
        username = self.vk.users.get(user_ids=send_to)['response']['first_name']
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message=f'Здравствуйте, {username}! Какой препарат вам необходимо найти?')
