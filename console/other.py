import os
from config import Config


def del_DF(file_name, dir_name):
    for root, dirs, files in os.walk(Config.FILE_PATH_ROOT, topdown=False):
        if file_name in files:
            os.remove(os.path.join(root, file_name))
        if dir_name in dirs:
            os.rmdir(os.path.join(root, dir_name))
