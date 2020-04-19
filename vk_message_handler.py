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

            if users.get(user_id, 'not_started') == 'not_started':
                users_info[user_id] = list()
                bot.start(user_id)
                users[user_id] = 'waiting_for_medicine'

            elif users[user_id] == 'waiting_for_medicine':
                users_info[user_id].append(msg['text'])
                bot.ask_for_location(user_id)
                users[user_id] = 'waiting_for_location'

            elif users[user_id] == 'waiting_for_location' and 'location' in msg['payload']:
                users_info[user_id].append(msg['geo'])
                del users[user_id]
                bot.send_results(user_id, users_info[user_id])
                del users_info[user_id]

            elif users[user_id] == 'waiting_for_location' and 'wait_for_city' in msg['payload']:
                bot.ask_city(user_id)
                users[user_id] = 'waiting_for_city'

            elif users[user_id] == 'waiting_for_city':
                users_info[user_id].append(msg['text'])
                del users[user_id]
                bot.send_results(user_id, users_info[user_id])
                del users_info[user_id]


if __name__ == '__main__':
    message_handler(VK_BOT_TOKEN, VK_BOT_ID)
