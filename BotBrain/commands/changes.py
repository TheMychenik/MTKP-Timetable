from .. import command_system
from .. import sql as sqlapi
from ..utils import text_to_img as img


def changes_(user_id, _):
    with sqlapi.mysqlapishit() as db:  # доступ к бд
        last_group = db.userdata.get_saved_group(user_id)  # поиск сохраненой пользователем группы
        if not last_group:
            return 'Не нашел вашу группу, напишите мне ее имя и я запомню.', ('text',)

        changes_date = db.sysdata.get_changes_date()  # дата последних замен
        lessons_from_db = db.changes.get(last_group)  # массив с данными замен

    if lessons_from_db:
        islef = bool(lessons_from_db[1])
        lefort = '(Лефортово)' if islef else ''

        lessons = f'{last_group} {lefort}\n' \
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
    else:
        errormsg = f"Замены на {changes_date}\n для {last_group} не найдены!"
        return errormsg, ('text',)

    path = img.create_photo(user_id, lessons, islef)
    return lessons, ('photo', path)


changes_command = command_system.Command()

changes_command.keys = ['замены']
changes_command.description = 'Отправлю вам самые свежие замены.'
changes_command.process = changes_
