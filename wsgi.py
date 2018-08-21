import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))

sys.path.append(basedir)
# 添加virtualenv的模块目录到系统路径
#windows
venv_path = os.path.join(basedir, 'venv\Lib\site-packages')
sys.path.append(venv_path)

from console.manage import app as application
