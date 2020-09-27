import os
import urllib.request

# TODO рефакторинг если нужно + комментарии добавить


def download(url, file_name, path):
    """
    :param url: ссылка на скачивание
    :param file_name: имя файла для сохранения
    :param path: путь для сохранения
    :return: путь к файлу
    """
    file_path = os.path.join(path, file_name)
    urllib.request.urlretrieve(url, file_path)
    return file_path


def remove_folder_contents(path):
    files = os.listdir(path)
    for file in files:
        try:
            os.remove(os.path.join(path, file))
        except OSError:
            continue
