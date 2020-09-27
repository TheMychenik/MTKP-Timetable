import os

import git
from flask import Flask, request, json
from loguru import logger

from BotBrain.changesAndScheduleParser import parse
from BotBrain import messageHandler
from BotBrain.VkApi import VkApi
from settings import vk, dirs, preinstallations

app = Flask(__name__)
preinstallations()

logger.add(os.path.join(dirs['logs'], 'Bot.txt'),
           format='{time: DD.MM.YYYY at HH:mm:ss} | {module} | {level} | {message}',
           rotation='3 days', backtrace=False, diagnose=False)

# stores last 5 messages ids i need it to exclude repeated messages
last_event_ids = ['']

last_updating_lessons_time = 0


@app.route('/')
def hello_world():
    return 'Hello there!'


@app.route('/vkcallback', methods=['POST'])
def vkbot():
    """Проверка валидности запроса от вк и выбор ответа"""
    data = json.loads(request.data)
    if 'type' not in data.keys() or data['secret'] != vk['secret_key']:
        return 'not vk'
    try:
        if data['type'] == 'confirmation':
            return callback_confirmation(data['group_id'])

        elif data['type'] == 'message_new' and data['event_id'] not in last_event_ids:
            # Пришло новое сообщение
            messageHandler.create_answer(data['object'], vk['token'])
            append_last_eventid(data['event_id'])
            return 'ok'

    except Exception as err:  # TODO нормальный перехват ошибок
        logger.exception(err)
        return 'error'


@app.route('/vkcallbacktimer', methods=['POST'])  # TODO купить бы хостинг, а не гемороиться с такими костылями
def updateschedule():
    data = json.loads(request.data)
    if 'type' not in data.keys() or data['secret'] != vk['timersecret_key']:
        return 'not vk'

    if data['type'] == 'confirmation':
        return callback_confirmation(data['group_id'])

    elif data['type'] == 'wall_post_new' and data['event_id'] not in last_event_ids:
        """В группе в вк выкладывается пост, если его текст !lessons, то выполняется парсинг. 
        Потом пост удаляется и создается новый с отложенной публикацией на 30 минут. Такой таймер...
        Затем проверка, что новый запрос пришел не раньше чем через 15 мин от прошлого."""

        global last_updating_lessons_time
        unix_fiveteen_minutes = 900
        time_from_last_request = int(data['object']['date']) - int(last_updating_lessons_time)
        print(time_from_last_request)

        if time_from_last_request > unix_fiveteen_minutes and data['object']['text'] == '!lessons':

            parse()

            last_updating_lessons_time = data['object']['date']
            append_last_eventid(data['event_id'])

            vkapi = VkApi(vk['user_token']).get_api()

            vkapi.wall.delete(owner_id=data['object']['owner_id'],
                              post_id=data['object']['id'])

            thirty_minutes_of_unixtime = 1800
            vkapi.wall.post(owner_id=vk['timerbotgroup_id'],
                            message='!lessons',
                            publish_date=data['object']['date'] + thirty_minutes_of_unixtime)
    return 'ok'


@app.route('/update_server', methods=['POST'])
def gitwebhook():
    # Делает pull из git репозитория и перезагружает бота
    if request.method == 'POST':
        try:
            repo = git.Repo(dirs['gitrepo'])
            origin = repo.remotes.origin
            origin.pull()
            logger.info('( Git ) Updated PythonAnywhere successfully')
            return 'Updated PythonAnywhere successfully', 200
        except Exception as err:
            logger.exception(f'( Git ) {err}')
    else:
        logger.info('( Git ) Wrong event type')
        return 'Wrong event type', 400


def append_last_eventid(eventid: str):
    """
    Добовляет id события в массив и следит чтобы было не больше 5
    :param eventid:
    """
    last_event_ids.append(eventid)
    if len(last_event_ids) > 5:
        last_event_ids.pop(0)


def callback_confirmation(group_id):
    # Если вк требует подтверждение сервера
    try:
        logger.info(f'Сonfirmation request received for group: {group_id}')
        # через vkapi получет код подтверждения и отправляет его вк
        vkapi = VkApi(vk['user_token']).get_api()
        confirmation_token = vkapi.groups.getCallbackConfirmationCode(group_id=group_id)
        logger.info(f'Сonfirmation token: {confirmation_token}')
    except Exception as err:  # TODO нормальный перехват ошибок
        logger.opt(exception=True).error(err)
    else:
        return confirmation_token['code']
