from settings import vk
from BotBrain.VkApi import VkApi
from loguru import logger


def __getdata(posts, changes: bool):
    """
    Ищет пост с заменами или расписанием

    :param posts: list
        массив постов по которым будет произведен поиск
    :param changes: bool
        искать замены или расписание,
        при True ищет замены с определенным названием и расширением файла,
        при False ищет расписание с определенным названием и расширением файла
    :return: str, tuple
        при успеном выполнении возвращает строку с ссылкой на файл и его название,
        иначе объекты None
    """

    filenames = ('замены',)
    filetypes = ('docx',)
    if not changes:
        filenames = ('мткп_', 'mtkp_')
        filetypes = ('xlsx',)

    for post in posts['items']:
        if post.__contains__('attachments'):
            for content in post['attachments']:
                if content['type'] == 'doc':
                    name = content['doc']['title'].lower()
                    doctype = content['doc']['ext']
                    if doctype in filetypes and name.startswith(filenames):
                        # составление ссылки
                        url = f"https://m.vk.com/doc{content['doc']['owner_id']}_{content['doc']['id']}"
                        return url, name
    else:
        return None, None


def get_url():
    """
    Возвращает массивы с ссылками и названиями файлов расписания и замен

    :return: tuple, tuple
    """
    try:
        # доступ к api
        vkapi = VkApi(vk['user_token']).get_api()
        # выборка последних постов в группе
        posts = vkapi.wall.get(owner_id=vk['mtkpgroup_id'], filter='owner', count=10)
    except VkApi.exceptions().ApiError as err:
        logger.exception(err)
        return (None, None), (None, None)
    else:
        changes_data = __getdata(posts, changes=True)
        schedule_data = __getdata(posts, changes=False)
        return changes_data, schedule_data
