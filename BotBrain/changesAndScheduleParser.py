from loguru import logger
from settings import dirs
from . import parsing
from . import sql as sqlapi

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
    userid_and_pathtoimg = []
    with sqlapi.mysqlapiwrapper() as db:

        data = db.userdata.get_all_mailing()
        logger.info('Пользовователи ', data)
        print(data)

        groups_with_changes = db.changes.get_all_groups()
        logger.info('Группы ', groups_with_changes)

        # for d in data:
        #     pass
