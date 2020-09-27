from loguru import logger
from settings import dirs, vk
from . import parsing
from .VkApi import VkApi
from . import sql as sqlapi
from .utils import text_to_img as img
# TODO  рефакторинг + комментарии


def parse():
    # заполняет замены и расписание в бд (отчищая предыдущие)
    with sqlapi.mysqlapiwrapper() as db:
        changes_last_url = db.sysdata.get_changes_last_url()
        schedule_last_url = db.sysdata.get_schedule_last_url()

    changes_data, schedule_data = parsing.get_url()  # (url, filename) 2x

    if changes_data[0] is not None and changes_data[0] != changes_last_url:
        path = parsing.download(f'{changes_data[0]}', changes_data[1], path=dirs['docs'])
        parsing.update_changes(path, changes_data[1])
        with sqlapi.mysqlapiwrapper() as db:
            db.sysdata.update_changes_last_url(changes_data[0])

    if schedule_data[0] is not None and schedule_data[0] != schedule_last_url:
        path = parsing.download(f'{schedule_data[0]}', schedule_data[1], path=dirs['docs'])
        parsing.update_schedule(path)
        with sqlapi.mysqlapiwrapper() as db:
            db.sysdata.update_schedule_last_url(schedule_data[0])

    parsing.remove_folder_contents(path=dirs['docs'])
    parsing.remove_folder_contents(path=dirs['images'])

    mailing()


def mailing():
    """Рассылает замены всем кто включил эту опцию исходя из сохраненной группы"""
    with sqlapi.mysqlapiwrapper() as db:

        groups_with_changes = db.changes.get_all_groups()  # все группы с заменами
        changes_date = db.sysdata.get_changes_date()  # дата последних замен

        for group in groups_with_changes:
            db.cursor.execute(f"SELECT userid FROM userdata WHERE mailing='1' AND savedgroup='{group}';")
            userids_ditry = db.cursor.fetchall()
            if len(userids_ditry) == 0:
                continue
            userids = []
            for row in userids_ditry:
                userids.append(row[0])

            lessons_from_db = db.changes.get(group)

            islef = bool(lessons_from_db[1])
            lefort = '(Лефортово)' if islef else ''

            lessons = f'{group} {lefort}\n' \
                      f'Замены на {changes_date}\n\n' \
                      f'Пара 1: {lessons_from_db[2]}\n' \
                      f'Кабинет: ({lessons_from_db[3]})\n' \
                      f'Пара 2: {lessons_from_db[4]}\n' \
                      f'Кабинет: ({lessons_from_db[5]})\n' \
                      f'Пара 3: {lessons_from_db[6]}\n' \
                      f'Кабинет: ({lessons_from_db[7]})\n' \
                      f'Пара 4: {lessons_from_db[8]}\n' \
                      f'Кабинет: ({lessons_from_db[9]})\n' \
                      f'Пара 5: {lessons_from_db[10]}\n' \
                      f'Кабинет: ({lessons_from_db[11]})\n' \
                      f'Пара 6: {lessons_from_db[12]}\n' \
                      f'Кабинет: ({lessons_from_db[13]})\n'

            path = img.create_photo(group, lessons, islef)
            vks = VkApi(vk['token'])
            vks.photo_msg(peer_id=userids, path_to_photo=path)



