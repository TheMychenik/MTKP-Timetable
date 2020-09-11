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

    logger.info('Checking for new doc links')
    changes_data, schedule_data = parsing.geturl()  # (url, filename) 2x
    
    if changes_data[0] is not None and changes_data[0] != changes_last_url:
        logger.info('Updating changes')
        path = parsing.download(f'{changes_data[0]}', changes_data[1], path=dirs['docs'])
        logger.info('Downloaded')
        parsing.update_changes(path, changes_data[1])
        logger.info('Changes table updated')
        with sqlapi.mysqlapiwrapper() as db:
            db.sysdata.update_changes_last_url(changes_data[0])
            logger.info('Changes url and date updated')

    if schedule_data[0] is not None and schedule_data[0] != schedule_last_url:
        logger.info('Updating schedule')
        path = parsing.download(f'{schedule_data[0]}', schedule_data[1], path=dirs['docs'])
        logger.info('Downloaded')
        parsing.update_schedule(path)
        logger.info('Schedule table updated')
        with sqlapi.mysqlapiwrapper() as db:
            db.sysdata.update_schedule_last_url(schedule_data[0])
            logger.info('Schedule url updated')

    parsing.remove_folder_contents(path=dirs['docs'])
    parsing.remove_folder_contents(path=dirs['images'])
