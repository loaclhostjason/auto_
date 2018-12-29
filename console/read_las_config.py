# -*- coding: utf-8 -*-
import xlrd
import os


def read_excel(path, file):
    result = []
    file_path = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(file_path, 'SV71_VDS.xlsx')
    if not file:
        excel_file = xlrd.open_workbook(file_path)
    else:
        excel_file = xlrd.open_workbook(path)

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
