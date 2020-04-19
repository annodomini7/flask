import random
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class VkBotReplies:
    """Этот класс содержит методы, отвечающие за, как иронично, ответы бота."""
    def __init__(self, vk_session):    # служебный метод: инициализация экземпляра класса + создание клавиатур
        self.vk = vk_session.get_api()

        self.location_keyboard = VkKeyboard(one_time=True)
        self.location_keyboard.add_location_button(payload={'button': 'location'})
        self.location_keyboard.add_line()
        self.location_keyboard.add_button('Указать город', payload={'button': 'wait_for_city'})

    def start(self, send_to):    # Первое сообщение, приветствие и вопрос о лекарстве
        username = self.vk.users.get(user_ids=send_to)[0]['first_name']
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message=f'Здравствуйте, {username}! Какой препарат вам необходимо найти?')

    def ask_for_location(self, send_to):    # Запрос местоположения или запрос города - зависит от выбора пользователя
        keyboard = self.location_keyboard.get_keyboard()
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

    def send_results(self, send_to, info):    # Высылает результат. Пока что работает в тестовом режиме.
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message=f'Вот то, что нам удалось найти!\n{info}')
