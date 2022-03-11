# -*- coding: utf-8 -*-
"""
VCIA
for python 3
@author: igor bertyaev

программа для расчета таблицы негабаритов и подготовки данных для QGIS

на вход файлы
- not gabarit.txt - насчитанные террасканом
- stow.pts
- имя_линии_specification.xlsx (XLSX ! - спецификация)

формируется выходная таблица установленного образца
программа также удаляет дублирующиеся координаты нерушений,
оставляя одно значение с наименьшим габаритом

для QGIS формируется набор данных с помощью которых затем строится атлас изображений

"""

from pathlib import Path
import openpyxl
from math import sqrt

# paths to files
p = Path(r'D:\work\_TP\test\vcia\635')  #work dir
p_str = p / '635_BLN-KIK-A_cgtow.pts'
spec = p / '635_BLN-KIK-A_Specification_St1.xlsx'


def centerline(p_str):
    # чтение файла координат опор c рабочей нумерацией и запись его в лист c с удалением дубликатов
    str = []  # list of structures
    with open(p_str) as ffile:
        for line in ffile:
            stroka = line.strip('\n').split()
            # ctow file should contain work-id, x, y, z in each row
            if len(stroka) == 4:
                # check if coords already in list (delete doubles with different names)
                dub = 0
                for i in range(len(str)):
                    # compare x y z written in list
                    if (str[i][1], str[i][2], str[i][3]) == (float(stroka[1]), float(stroka[2]), float(stroka[3])):
                        dub +=1
                if dub < 1:
                    # if there are no such coords, we can write new one
                    str.append([int(stroka[0]), float(stroka[1]), float(stroka[2]), float(stroka[3])])
            elif len(stroka) == 0:
                # if there is blank stroke in the file
                print('blank')
            else:
                # if stroke looks weird
                print('ctow file error')

    print(f'загружено опор: {len(str)}')
    #print(str)

    return str


def spec_id(spec):
    # reading specification and save work and id names of structures
    id_tows = []  # creating list * work id, id *
    wb = openpyxl.load_workbook(spec)
    sheet = wb.active

    for cn in range(3, sheet.max_row):   ## cn - cell number
        if sheet['A' + (str(cn))].value != sheet['A' + (str(cn + 1))].value:
            if isinstance(sheet['A' + (str(cn))].value, int):
                id_tows.append([int(sheet['A' + (str(cn))].value), str(sheet['B' + (str(cn))].value)])
        else:
            break

    return id_tows


ids = spec_id(spec)
print(ids[:4])
print(ids[-4:])





# TODO - чтение спецификации - добавление ид-номеров опор
# TODO - разбиение на центрлайны (создать лист последовательностей опор - из спецификации)
# TODO - чтение файлов негабаритов - создание таблицы
# TODO - вывод таблицы негабаритов в xls
# TODO - интерфейс
# TODO - таблица под qgis - пролеты с негабаритами, негабаритные точки, длины пролетов
# TODO - добавить обрезку длинных пролетов
