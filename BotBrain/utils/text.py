import re


def find_group_name(group_file_name):
    group_file_name = group_file_name.split('(')
    return group_file_name[0].strip()


def find_date_from_text(msg):
    data = re.search(r'\d{1,2}\.\d{1,2}', msg)
    if data is not None:
        return data.group(0)
    else:
        return 'Дата не найдена'


def clear_invisible_character(dirty_str, separator=''):  # удаляет непечатаемые символы из строки
    clear_str = re.sub(r'[\s]', separator, dirty_str)
    return clear_str.strip()


def check_for_group_tag(message):
    group = message.replace(' ', '')
    if group.startswith(('Т', 'т')) and 8 > len(group) >= 4:
        if group.find('-') != -1:
            return group.upper()
        else:
            for char in range(len(group)):
                if group[char].isdigit():
                    group = group[:char] + '-' + group[char:]
                    break
            return group.upper()
    else:
        return False
