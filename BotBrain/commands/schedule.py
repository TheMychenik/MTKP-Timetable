from .. import command_system
from .. import sql as sqlapi
from ..utils import week_and_date as weekday
from ..utils import text_to_img as img


def schedule_(user_id, message):
    with sqlapi.mysqlapishit() as db:  # доступ к бд
        last_group = db.userdata.get_saved_group(user_id)  # поиск сохраненой пользователем группы
        if not last_group:
            return 'Не нашел вашу группу, напишите мне ее имя и я запомню.', ('text',)

        day = weekday.day_of_week_by_name(message)  # номер дня недели на основе сообщения (сегодня, завтра, пн, вт)
        if day == 7:
            return 'В воскресенье отдыхаем от пар.', ('text',)

        week = weekday.get_week(day)  # верхняя/нижняя неделя
        isupper = True if week == 'Верхняя' else False
        lessons_from_db = db.schedule.get(last_group, isupper=isupper, day=day)

    if lessons_from_db:
        islef = bool(lessons_from_db[1])
        lefort = '(Лефортово)' if islef else ''

        lessons = f'{last_group} {lefort}\n' \
                  f'{week} неделя\n' \
                  f'Расписание на {weekday.context_days.get(day)}\n\n' \
                  f'Пара 1: {lessons_from_db[4]}\n' \
                  f'Кабинет: ({lessons_from_db[5]})\n' \
                  f'Пара 2: {lessons_from_db[6]}\n' \
                  f'Кабинет: ({lessons_from_db[7]})\n' \
                  f'Пара 3: {lessons_from_db[8]}\n' \
                  f'Кабинет: ({lessons_from_db[9]})\n' \
                  f'Пара 4: {lessons_from_db[10]}\n' \
                  f'Кабинет: ({lessons_from_db[11]})\n' \
                  f'Пара 5: {lessons_from_db[12]}\n' \
                  f'Кабинет: ({lessons_from_db[13]})\n' \
                  f'Пара 6: {lessons_from_db[14]}\n' \
                  f'Кабинет: ({lessons_from_db[15]})\n'
    else:
        errormsg = f'Расписание для {last_group} не найдено, проверьте правильность написания группы ' \
                   'или обратитесь к разработчику бота.'
        return errormsg, ('text',)

    path = img.create_photo(user_id, lessons, islef)
    return lessons, ('photo', path)


schedule_command = command_system.Command()

schedule_command.keys = ['завтра', 'сегодня',
                         'понедельник', 'пн', 'вторник', 'вт',
                         'среда', 'ср', 'четверг', 'чт',
                         'пятница', 'пт', 'суббота', 'сб',
                         'воскресенье', 'вс']
schedule_command.description = 'Отправлю расписание на сегодня или завтра. Так же можете прислать мне название дня ' \
                               'недели в полной или сокращенной форме (Пример: понедельник или пн).'
schedule_command.process = schedule_
