import importlib
import os

from . import sql as sqlapi
from .VkApi import VkApi
from .command_system import command_list
from .utils import text


def load_modules():
    """Импортирует все модули с командами бота из /BotBrain/commands/"""

    command_files = os.listdir("BotBrain/commands")
    modules = filter(lambda x: x.endswith('.py'), command_files)
    for m in modules:
        importlib.import_module("BotBrain.commands." + m[0:-3])


def request_recognizer(user_id, message):
    """
    Выделяет команду из сообщения и передает на выполнение ответственному модулю

    :param user_id: str or int
    :param message: str
    :return: tuple(str, tuple(str, bool))
    """

    answer = "Не понял вас. Напиши 'помощь', чтобы узнать мои команды", ('text',)
    for command in command_list:
        if message in command.keys:
            answer = command.process(str(user_id), message)
        else:
            group = text.check_for_group_tag(message)
            if group:
                with sqlapi.mysqlapiwrapper() as db:
                    db.userdata.update_saved_group(str(user_id), group)
                answer = 'Запомнил! Теперь выбирайте, что хотите узнать.', ('text',)
    return answer


def create_answer(data, token):
    """
    Создает и отправляет ответ пользователю
    :param data: dict
    :param token: str
    """
    load_modules()
    vk = VkApi(token)
    user_id = data['peer_id']
    message = data['text'].lower()

    answer, attachment = request_recognizer(user_id, message)
    if attachment[0] == 'text':
        vk.text_msg(user_id, answer, keyboard=vk.keyboard_main)
    elif attachment[0] == 'photo':
        vk.photo_msg(user_id, path_to_photo=attachment[1])
