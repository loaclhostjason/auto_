# -*- coding: utf-8 -*-
import xlrd
from app import create_app
from flask import current_app
from app.manage.models import Las

app = create_app()
app.app_context().push()


def read_excel(project_name=None):
    path = current_app.config['LAS_FILE_PATH_ROOT']
    result = []
    las = Las.query.filter_by(project_name=project_name).first()
    if not las:
        excel_file = xlrd.open_workbook('./SV71_VDS.xlsx')
    else:
        
    table = excel_file.sheets()[0]
    nrows = table.nrows
    for i in range(nrows):
        if i == 0:
            continue
        line = table.row_values(i)
        if line[0]:
            try:
                result.append({str(int(line[0])): line[1]})
            except Exception as e:
                result.append({str(line[0]): line[1]})
    return result


if __name__ == '__main__':
    read_excel()
