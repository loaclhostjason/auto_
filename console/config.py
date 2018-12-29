# -*- coding:utf8 -*-
import os
import json


class ReadConfigJson(object):

    def __init__(self):
        path = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(path, 'config.json')
        self.config_path = config_path

    def __read_json(self):
        with open(self.config_path, encoding='utf-8') as f:
            data = f.read()
            data = json.loads(data)
        return data

    def get_mysql_config(self):
        mysql_dict = self.__read_json()['mysql']
        mysql_url = 'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(user=mysql_dict['user'],
                                                                                        password=mysql_dict['password'],
                                                                                        host=mysql_dict['host'],
                                                                                        port=mysql_dict['port'],
                                                                                        database=mysql_dict['database'])

        return mysql_url


base_path = os.path.abspath(os.path.dirname(__file__))
upload_path = os.path.join(base_path, 'upload', 'projects')

file_path_root = os.path.join(base_path, 'files')
file_path = os.path.join(file_path_root, 'all')
part_file_path = os.path.join(file_path_root, 'part')

las_path_root = os.path.join(base_path, 'las_file')
json_path = os.path.join(base_path, 'json_file')

if not os.path.exists(file_path):
    os.makedirs(file_path)

if not os.path.exists(part_file_path):
    os.makedirs(part_file_path)

if not os.path.exists(las_path_root):
    os.makedirs(las_path_root)

if not os.path.exists(json_path):
    os.makedirs(json_path)


class Config:
    DEBUG = True
    # SECRET_KEY = os.urandom(24)
    SECRET_KEY = 'tc'

    SQLALCHEMY_DATABASE_URI = ReadConfigJson().get_mysql_config()
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    BOOTSTRAP_SERVE_LOCAL = True
    FLASKY_PER_PAGE = 20

    BABEL_DEFAULT_LOCALE = 'zh_Hans_CN'

    ASSETS_DEBUG = False

    UPLOADS_DEFAULT_DEST = upload_path
    FILE_PATH = file_path
    FILE_PATH_ROOT = file_path_root
    PART_PATH_ROOT = part_file_path

    LAS_FILE_PATH_ROOT = las_path_root

    JSON_FILE_PATH = json_path

    DEFAULT_BIT = '00000000'

    @staticmethod
    def init_app(app):
        pass
