import random


class VkBotReplies:
    """Этот класс содержит методы, отвечающие за, как иронично, ответы бота."""
    def __init__(self, vk_session):    # служебный метод
        self.vk = vk_session.get_api()

    def create_keyboard(self, *labels, one_time=True):    # служебный метод формирования клавиатуры
        keyboard = {'one_time': one_time,
                    'buttons': [[] for x in range(len(labels))]}
        for label in enumerate(labels):
            payload = r'{\"button\": \"' + str(label[0] + 1) + r'\"}'
            if label[1] == 'SEND_LOCATION':
                keyboard['buttons'][label[0]].append({'action': {'type': 'location',
                                                                 'payload': payload}})
            else:
                keyboard['buttons'][label[0]].append({'action': {'type': 'text',
                                                                 'payload': payload,
                                                                 'label': label[1]},
                                                      'color': 'primary'})
        return str(keyboard).replace("'", '"').replace('True', 'true').replace('False', 'false')

    def start(self, send_to):    # Первое сообщение, приветствие и вопрос о лекарстве
        username = self.vk.users.get(user_ids=send_to)['response']['first_name']
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message=f'Здравствуйте, {username}! Какой препарат вам необходимо найти?')

    def ask_for_location(self, send_to):    # Запрос местоположения или запрос города - зависит от выбора пользователя
        keyboard = self.create_keyboard('SEND_LOCATION', 'Указать город')
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
