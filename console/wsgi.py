import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))

sys.path.append(basedir)
# 添加virtualenv的模块目录到系统路径
sys.path.append('/usr/local/auto_/venv/lib64/python3.4/site-packages')



from app import app as application
