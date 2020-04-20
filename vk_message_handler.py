import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_bot_replies import VkBotReplies


VK_BOT_ID = 000000000
VK_BOT_TOKEN = 'token'


def message_handler(token, id):
    users = dict()
    users_info = dict()

    vk_session = vk_api.VkApi(token=token)
    bot = VkBotReplies(vk_session)
    longpoll = VkBotLongPoll(vk_session, id)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.object.message['from_id']
            msg = event.object.message
            try:
                if users.get(user_id, 'not_started') == 'not_started':
                    users_info[user_id] = list()
                    bot.start(user_id)
                    users[user_id] = 'waiting_for_medicine'

                elif users[user_id] == 'waiting_for_medicine':
                    users_info[user_id].append(msg['text'])
                    if (('location' in event.obj.client_info['button_actions'] and
                         'text' in event.obj.client_info['button_actions'])):
                        bot.ask_for_location(user_id)
                        users[user_id] = 'waiting_for_location'
                    else:
                        bot.ask_city(user_id)
                        users[user_id] = 'waiting_for_city'

                elif users[user_id] == 'waiting_for_location' and 'location' in msg['payload']:
                    users_info[user_id].append(msg['geo'])
                    del users[user_id]
                    bot.send_results(user_id, users_info[user_id])
                    del users_info[user_id]

                elif users[user_id] == 'waiting_for_location' and 'указать город' in msg['text'].lower():
                    bot.ask_city(user_id)
                    users[user_id] = 'waiting_for_city'

                elif users[user_id] == 'waiting_for_city':
                    users_info[user_id].append(msg['text'])
                    del users[user_id]
                    bot.send_results(user_id, users_info[user_id])
                    del users_info[user_id]
            except Exception as e:
                bot.return_error(user_id, e)
                if not users.get(user_id, None) is None:
                    del users[user_id]
                if not users_info.get(user_id, None) is None:
                    del users_info[user_id]


if __name__ == '__main__':
    message_handler(VK_BOT_TOKEN, VK_BOT_ID)
