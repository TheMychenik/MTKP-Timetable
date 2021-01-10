import datetime

"""Дни недели в винительном падеже"""
context_days = {1: 'понедельник', 2: 'вторник', 3: 'среду', 4: 'четверг', 5: 'пятницу', 6: 'субботу', 7: 'воскресенье'}

"""Дни недели в именительном падеже"""
named_days = {('пн', 'понедельник'): 1, ('вт', 'вторник'): 2,
              ('ср', 'среда'): 3, ('чт', 'четверг'): 4,
              ('пт', 'пятница'): 5, ('сб', 'суббота'): 6,
              ('вс', 'воскресенье'): 7}


def day_of_week_by_name(day_name: str):  # day_name: str(сегодня или завтра или день недели)
    """
    Принимает строку сегодня, завтра, сокращенное или полное название дня недели
    в именительный падеже и возвращает его порядковый номер
    от 1 (Понедельник) до 7 (Воскресенье) включительно

    :param day_name: str
    :return: int
    """

    today = datetime.date.today()

    if day_name == 'сегодня':
        return today.isoweekday()
    elif day_name == 'завтра':
        tomorrow = today + datetime.timedelta(days=1)
        return tomorrow.isoweekday()
    else:
        for days in named_days:
            if day_name in days:
                return named_days.get(days)


def day_of_week_by_num(day_num: int):
    """
    Принимает номер дня недели от 1 (Понедельник) до 7 (Воскресенье) включительно
    и возвращает его полное название

    :param day_num: int
    :return: str
    """

    key_list = list(named_days.keys())
    val_list = list(named_days.values())
    return key_list[val_list.index(day_num)][1]


def check_isweek_upper(compare_day: int):
    """
    Определяет верхняя или нижняя неделя по ее номеру

    :param compare_day: int
        Если переданный номер дня недели меньше сегоднящнего, то используется следующая неделя
    :return: bool
    """
    weeknum = datetime.datetime.now().isocalendar()[1]
    if compare_day < datetime.date.today().isoweekday():
        weeknum += 1
    return False if weeknum % 2 == 0 else True
