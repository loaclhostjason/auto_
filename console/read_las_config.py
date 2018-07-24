# -*- coding: utf-8 -*-
import xlrd


def read_excel():
    result = []
    excel_file = xlrd.open_workbook('./SV71_VDS.xlsx')
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
