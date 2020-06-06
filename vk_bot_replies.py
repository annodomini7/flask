import random
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class VkBotReplies:
    """Этот класс содержит методы, отвечающие за, как иронично, ответы бота."""

    def __init__(self, vk_session):  # служебный метод: инициализация экземпляра класса + создание части клавиатур
        self.vk = vk_session.get_api()

        self.location_keyboard = VkKeyboard(one_time=True)
        self.location_keyboard.add_button('Указать город',
                                          color=VkKeyboardColor.PRIMARY)
        self.location_keyboard.add_line()
        self.location_keyboard.add_button('Изменить выбор препарата',
                                          color=VkKeyboardColor.NEGATIVE)
        self.again_keyboard = VkKeyboard(one_time=True)
        self.again_keyboard.add_button('Посмотреть в другом городе',
                                       color=VkKeyboardColor.PRIMARY)
        self.again_keyboard.add_line()
        self.again_keyboard.add_button('Больше не нужно',
                                       color=VkKeyboardColor.NEGATIVE)

    def help(self, send_to):
        help_msg = 'Введите название лекарства, правильно ответьте на мои вопросы и узнайте, ' \
                   'где можно купить интересующий Вас препарат.\n' \
                   'На данный момент я знаю только лекарства, ' \
                   'предназначенные для лечения заболевания респираторной системы ' \
                   '(по классификации АТХ).\n\n' \
                   '"Тут должно быть что-то умное и полезное"\n' \
                   '© подвал нашего сайта\n\n' \
                   '[id331822495|Коган Анна]: разработчик █████\n' \
                   '[id251482329|Матевосян Артем]: разработчик [ДАННЫЕ УДАЛЕНЫ]'
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message=help_msg)

    def start(self, send_to):  # Первое сообщение, приветствие и вопрос о лекарстве
        username = self.vk.users.get(user_ids=send_to)[0]['first_name']
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message=f'Здравствуйте, {username}! Какой препарат Вам необходимо найти? '
                                      f'Напишите его название кириллицей.\nТакже вы можете в любой момент вызвать справку, '
                                      f'написав "помощь" без кавычек.')

    def clarify_name(self, send_to, names):
        clarify_keyboard = VkKeyboard(one_time=True)
        clarify_keyboard.add_button(names[0])
        for name in names[1:]:
            clarify_keyboard.add_line()
            clarify_keyboard.add_button(name)
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message='Я нашёл что-то в базе данных. Выберите тот препарат, который Вы ищете.',
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

    def location_or_cancel(self, send_to, user):  # Выбор между отправкой города и отменой выбора лекарства
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

    def ask_city(self, send_to):  # Спрашивает город
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message='Укажите свой город, чтобы я нашёл аптеки.')

    def send_results(self, send_to, info):  # Формирует и высылает результат.
        text = '\n\n'.join([f'★ {i[1]}\n'
                            f'Время работы: {i[3]}\n'
                            f'Адрес: {i[2]}\n'
                            f'Телефон: {i[4]}\n'
                            f'Цена: {int(float(i[5].replace(",", ".")))} рублей '
                            f'{int((float(i[5].replace(",", ".")) - int(float(i[5].replace(",", ".")))) * 100)} '
                            f'копеек\nhttps://maps.yandex.ru/?source=serp_navig&'
                            f'text={i[2].replace(', ', '%2C+)}'.replace("None", "неизвестно") for i in info])
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message=f'Вот то, что мне удалось найти!\n\n{text}')

    def shall_i_try_again(self, send_to):  # "Хотите, чтобы я поискал в другом городе?"
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message='Хотите, чтобы я поискал в другом городе?',
                              keyboard=self.again_keyboard.get_keyboard())

    def return_msg(self, send_to, msg):  # Присылает пользователю ошибки и сообщения, не требующие особых дополнений.
        self.vk.messages.send(peer_id=send_to,
                              random_id=random.randint(0, 2 ** 64),
                              message=f'{msg}')
