import mysql.connector.errors
from docx import Document

from .. import sql as sqlapi
from ..utils.text import clear_invisible_character, find_group_name, find_date_from_text
from loguru import logger

# TODO рефакторинг если нужно + комментарии добавить

all_lessons = []


def __find_row_with_group_name(tables):
    # Ищет имена групп в файле
    for tab in range(len(tables)):
        # Проходит по всем таблицам док-та поочередно
        for cell in range(len(tables[tab].rows[0].cells)):
            # А так же по рядам (строка всегда первая (0 для программы))
            if tables[tab].rows[0].cells[cell].text:
                # При нахождении совпадений возвращает № таблицы и № ряда
                # в нулевой ячеке находится время начала\конца пар, поэтому она пропускается
                if cell != 0:
                    __get_lessons(tables[tab], cell)


def __get_lessons(table, cell_index):  # Формирование списка замен
    row_index = 1  # номер строки
    lessons_dict = []
    group_file_name = clear_invisible_character(table.rows[0].cells[cell_index].text)  # Отчищаю имя группы из файла
    group_name = find_group_name(group_file_name)
    islef = True if group_name != group_file_name else False
    try:
        while row_index < len(table.rows):
            # if row_index % 2 != 0:  # (нечетная строка) В документе на нечетных строчках идут названия пар
            current_lesson_name = clear_invisible_character(table.rows[row_index].cells[cell_index].text, separator=' ')
            if current_lesson_name.find('отпущена') != -1:
                # если  на этой паре "группа отпущена", то это записывается в список, а кабинет не указывается
                lessons_dict.append(('!!!Группа отпущена!!!', ''))
                row_index += 2
            else:
                row_index += 1
                current_cabinet_number = clear_invisible_character(table.rows[row_index].cells[cell_index].text,
                                                                   separator='')
                lessons_dict.append((current_lesson_name, current_cabinet_number))
                row_index += 1

        if len(lessons_dict) < 6:  # если в масиве < 6 элементов (пара, кабинет)
            lessons_dict = [('Ошибка заполнения', 'Проверьте вручную')] * 6

        all_lessons.append([group_name, islef, lessons_dict])
    except IndexError:  # в душе не ебу, что за ошибки ниже. Хер знает, когда писал код
        print('index error')


def update_changes(path_to_file, file_name):
    doc = Document(path_to_file)
    tables = doc.tables
    __find_row_with_group_name(tables)
    with sqlapi.mysqlapishit() as db:
        try:
            db.changes.clear()
            for less in all_lessons:
                db.changes.insert(group=less[0], islef=less[1], lessons=less[2])
        except mysql.connector.errors.IntegrityError as err:
            logger.info(err)
        else:
            file_date = find_date_from_text(file_name)
            db.sysdata.update_changes_date(file_date)
