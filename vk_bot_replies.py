import random
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class VkBotReplies:
    """Этот класс содержит методы, отвечающие за, как иронично, ответы бота."""
    def __init__(self, vk_session):    # служебный метод: инициализация экземпляра класса + создание клавиатур
        self.vk = vk_session.get_api()

        self.location_keyboard = VkKeyboard(one_time=True)
        self.location_keyboard.add_button('Указать город', payload={'button': 'wait_for_city'})
        self.location_keyboard.add_line()
        self.location_keyboard.add_button('Изменить выбор препарата',
                                          payload={'button': 'cancel'},
                                          color=VkKeyboardColor.NEGATIVE)

    def start(self, send_to):    # Первое сообщение, приветствие и вопрос о лекарстве
        username = self.vk.users.get(user_ids=send_to)[0]['first_name']
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message=f'Здравствуйте, {username}! Какой препарат Вам необходимо найти? '
                              f'Напишите его название кириллицей.')

    def clarify_name(self, send_to, names):
        clarify_keyboard = VkKeyboard(one_time=True)
        clarify_keyboard.add_button(names[0])
        for name in names[1:]:
            clarify_keyboard.add_line()
            clarify_keyboard.add_button(name)
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message='Я нашёл несколько лекарств в базе данных. Выберите то, которое Вы ищете.',
                              keyboard=clarify_keyboard.get_keyboard())

    def ask_med_form(self, send_to, forms):
        form_keyboard = VkKeyboard(one_time=True)
        form_keyboard.add_button(forms[0])
        for form in forms[1:]:
            form_keyboard.add_line()
            form_keyboard.add_button(form)
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message='Выберите одну из известных мне форм выпуска.',
                              keyboard=form_keyboard.get_keyboard())

    def ask_dose(self, send_to, doses):
        dose_keyboard = VkKeyboard(one_time=True)
        dose_keyboard.add_button(doses[0])
        for dose in doses[1:]:
            dose_keyboard.add_line()
            dose_keyboard.add_button(dose)
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message='Выберите одну из известных мне дозировок.',
                              keyboard=dose_keyboard.get_keyboard())

    def location_or_cancel(self, send_to, user):    # Выбор между отправкой города и отменой выбора лекарства
        keyboard = self.location_keyboard.get_keyboard()
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message=f'Выбран препарат "{user.req_medicine}"\n'
                              f'Форма выпуска: {user.med_form}\n'
                              f'Дозировка: {user.dose}\n'
                              f'Укажите город, и я дам Вам список его аптек, '
                              f'где есть запрошенный препарат. '
                              f'Также вы можете сменить выбор лекарства.',
                              keyboard=keyboard)

    def ask_city(self, send_to):    # Спрашивает город
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message='Укажите свой город, чтобы я нашёл аптеки.')

    def send_results(self, send_to, info):    # Высылает результат. Пока что работает в тестовом режиме.
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message=f'Вот то, что мне удалось найти!\n{info}')

    def return_msg(self, send_to, msg):    # Метод, присылающий пользователю сообщения в нестандартных ситуациях.
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message=f'{msg}')
