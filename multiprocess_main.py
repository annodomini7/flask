from telegram_bot import main_tg
from vk_message_handler import main_vk
from main import main_site
from multiprocessing import Process


if __name__ == '__main__':
    procs = [Process(target=main_site), Process(target=main_vk), Process(target=main_tg)]
    for proc in procs:
        proc.start()
    for proc in procs:
        proc.join()
