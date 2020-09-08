import os
import urllib.request

# TODO рефакторинг если нужно + комментарии добавить


def download(url, file_name, path):
    file_path = os.path.join(path, file_name)
    urllib.request.urlretrieve(url, file_path)
    return file_path


def remove_folder_contents(path):
    files = os.listdir(path)
    for file in files:
        os.remove(os.path.join(path, file))
