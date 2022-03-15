# -*- coding: utf-8 -*-
"""
VCIA
for python 3
@author: igor bertyaev

программа для расчета таблицы негабаритов и подготовки данных для QGIS

на вход файлы
- not_gabarit_1.txt - насчитанные террасканом
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
    # reading xlsx specification and save work and id names of structures in list
    id_tows = []  # creating list * work id, id , num of cline *
    cline_num = 1   # number of cline
    wb = openpyxl.load_workbook(spec)
    sheet = wb.active

    for cn in range(3, sheet.max_row):   ## cn - cell number
        if sheet['A' + (str(cn))].value != sheet['A' + (str(cn + 1))].value:
            if isinstance(sheet['A' + (str(cn))].value, int):
                id_tows.append([int(sheet['A' + (str(cn))].value), str(sheet['B' + (str(cn))].value), cline_num])
            else:
                cline_num += 1   # change cline num after empty stroke in spec
        else:
            break

    return id_tows


def notgabread(p):
    # read notgab files and create tab without duplicate points and with num of cline
    # exit tab has 7 columns: span num (work ts), wire num, gab, x, y, z, num of cline.

    notgabfiles = list(p.glob('*gabarit*.txt'))    # list of input files
    ngtab = []    # table of notgabs

    for file in notgabfiles:
        cline_num = file.stem.split('_')[-1]   # number of cline is the end of filename

        with open(file) as ngfile:
            ngtab.append(ngfile.readline().strip('\n').split())    # first line - add it separately
            ngtab[-1].append(cline_num)    # add cline number to the first stroke
            for line in ngfile:
                stroka = line.strip('\n').split()
                stroka.append(cline_num)   # add cline number
                if stroka[0] == ngtab[-1][0]:
                    # check if same span has same gab point
                    tr = 0   # number of try
                    for pt in range(len(ngtab)):
                        if (stroka[3], stroka[4], stroka[5]) == (ngtab[pt][3], ngtab[pt][4], ngtab[pt][5]):
                            # if all coords the same
                            if stroka[2] < ngtab[pt][2]:
                                # check which one is smaller and keep it
                                ngtab[pt] = stroka
                        else:
                            tr += 1
                            if tr == len(ngtab):
                                # when we read all list and did not find same - take this
                                ngtab.append(stroka)
                else:
                    ngtab.append(stroka)

    return ngtab



def idspannames(id_tows, ngtab):
    # in ngtab we should add span names with work and real IDs

    for st in range(len(ngtab)):
        # first we found start of cline num
        tsn = int(ngtab[st][0])   # terrascan span num
        cn = int(ngtab[st][6])   # num of cline
        start_cn = 100000
        for str in range(len(id_tows)):
            if id_tows[str][2] == cn:
                if id_tows[str][0] < start_cn:
                    start_cn = id_tows[str][0]   # start of this cline

        wid = start_cn + tsn   # now we know work ID
        id_st, id_fin = '-', '-'   # start and finish ID names

        for str2 in range(len(id_tows)):
            # then found ID names
            if id_tows[str2][0] == wid:
                id_st = id_tows[str2][1]
                id_fin= id_tows[str2+1][1]

        # then add work_id, start_id and finish_ID to our table
        for a in [wid, id_st, id_fin]: ngtab[st].append(a)

    return ngtab


id_tows = spec_id(spec)
ngtab = notgabread(p)

new_tab = idspannames(id_tows, ngtab)

for i in range(len(new_tab)):
    print(new_tab[i])


# TODO - формат и расчет таблицы негабаритов
# TODO - вывод таблицы негабаритов в xlsx
# TODO - интерфейс
# TODO - таблица под qgis - пролеты с негабаритами, негабаритные точки, длины пролетов
# TODO - добавить обрезку длинных пролетов
