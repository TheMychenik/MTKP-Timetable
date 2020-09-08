import openpyxl
from loguru import logger

from .. import sql as sqlapi
from ..utils.text import clear_invisible_character, check_for_group_tag

ROW_WITH_GROUP_NAMES = 3
MAX_ROW = 75
LEFORTOVO_COLORS = ['FFE1FFE1', 'FFCCFFCC']


def __get_cab(sheet, cab_row, cab_column):
    cabinet = sheet.cell(row=cab_row, column=cab_column)
    if cabinet.value is not None:
        return clear_invisible_character(str(cabinet.value), separator='')
    else:
        return ''


def __find_cab_column(sheet, group_name, group_col):
    """Берет соседнюю справа ячейку от ячейки группы, если там повторяется имя группы, то берет следующую (макс 2),
        таким образом нахдится столбец с кабинетами"""
    for cabinet_cells in sheet.iter_rows(min_row=ROW_WITH_GROUP_NAMES, max_row=ROW_WITH_GROUP_NAMES,
                                         min_col=group_col + 1, max_col=group_col + 2):
        for cabinet_name in cabinet_cells:
            if cabinet_name.value is not None and not cabinet_name.value.startswith(group_name):
                return cabinet_name.column


def __get_lessons(sheet):
    last_group_name = ''
    all_lessons = []
    for group_names in sheet.iter_rows(min_row=ROW_WITH_GROUP_NAMES, max_row=ROW_WITH_GROUP_NAMES,
                                       max_col=sheet.max_column):
        # проходит по рядам с именами групп
        for group_name in group_names:
            # проверят имя группы фильром и на дублирование
            if group_name.value is not None and check_for_group_tag(group_name.value) \
                    and group_name.value != last_group_name:
                cabinet_col = __find_cab_column(sheet, group_name.value, group_name.column)
                last_group_name = group_name.value
                lessons_row = ROW_WITH_GROUP_NAMES + 1
                day = 1
                current_row = 0
                while current_row < MAX_ROW:
                    # цикл для вывода не всех пар сразу, а по 6 штук (один день)
                    upper = []
                    islefupper = False
                    lower = []
                    isleflower = False

                    for lessons in sheet.iter_rows(min_row=lessons_row, max_row=lessons_row + 11,
                                                   min_col=group_name.column, max_col=group_name.column):
                        for lesson_name in lessons:
                            if repr(lesson_name) == '<EmptyCell>':
                                if len(upper) <= len(lower):
                                    upper.append(('', ''))
                                else:
                                    lower.append(('', ''))
                            else:
                                # [group_name, day, isupper, islef, [(less_1, cab_1), ..., (less_6, cab_6)]]

                                isupper = False if lesson_name.row % 2 == 0 else True
                                if lesson_name.value is not None:
                                    lesson = clear_invisible_character(lesson_name.value, separator=' ')
                                    cab = __get_cab(sheet, lesson_name.row, cabinet_col)
                                    if isupper:
                                        islefupper = True if lesson_name.fill.start_color.rgb in LEFORTOVO_COLORS \
                                            else False
                                        upper.append((lesson, cab))
                                    else:
                                        isleflower = True if lesson_name.fill.start_color.rgb in LEFORTOVO_COLORS \
                                            else False
                                        lower.append((lesson, cab))
                                else:
                                    if isupper:
                                        upper.append(('', ''))
                                    else:
                                        lower.append(('', ''))

                                current_row = lesson_name.row

                    all_lessons.append({'group_name': last_group_name,
                                        'day': day,
                                        'isupper': True,
                                        'islef': isleflower,
                                        'lessons': upper})

                    all_lessons.append({'group_name': last_group_name,
                                        'day': day,
                                        'isupper': False,
                                        'islef': islefupper,
                                        'lessons': lower})
                    day += 1
                    lessons_row += 12
    return all_lessons


def update_schedule(path_to_file):
    logger.info('Parsing')
    wb = openpyxl.load_workbook(filename=path_to_file, read_only=True)
    sheet = wb[wb.sheetnames[0]]
    lessons_data = __get_lessons(sheet)

    with sqlapi.mysqlapishit() as db:
        db.schedule.clear()
        for data in lessons_data:
            db.schedule.insert(group=data['group_name'], day=data['day'], isupper=int(data['isupper']),
                               islef=int(data['islef']), lessons=data['lessons'])
    wb.close()


if __name__ == '__main__':
    update_schedule(path_to_file=(r'C:\Users\Леха\Desktop\GitHub\MTKP Timetable\docs\MTKP_20_1_semestr.xlsx'))