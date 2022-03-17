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


def centerline(path_str):
    # чтение файла координат опор c рабочей нумерацией и запись его в лист c с удалением дубликатов
    str = []  # list of structures
    with open(path_str) as ffile:
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

    return str


def spec_id(specification):
    # reading xlsx specification and save work and id names of structures in list
    id_tows = []  # creating list * work id, id , num of cline *
    cline_num = 1   # number of cline
    wb = openpyxl.load_workbook(specification)
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


def notgabread(path_to_folder):
    # read notgab files and create tab without duplicate points and with num of cline
    # exit tab has 7 columns: span num (work ts), wire num, gab, x, y, z, num of cline.

    notgabfiles = list(path_to_folder.glob('*gabarit*.txt'))    # list of input files
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


def idspannames(ids, notgabtab):
    # in ngtab we should add span names with work and real IDs

    for st in range(len(notgabtab)):
        # first we found start of cline num
        tsn = int(notgabtab[st][0])   # terrascan span num
        cn = int(notgabtab[st][6])   # num of cline
        start_cn = 100000
        for str in range(len(ids)):
            if ids[str][2] == cn:
                if ids[str][0] < start_cn:
                    start_cn = ids[str][0]   # start of this cline

        wid = start_cn + tsn   # now we know work ID
        id_st, id_fin = '-', '-'   # start and finish ID names

        for str2 in range(len(ids)):
            # then found ID names
            if ids[str2][0] == wid:
                id_st = ids[str2][1]
                id_fin= ids[str2 + 1][1]

        # then add work_id, start_id and finish_ID to our table
        for a in [wid, id_st, id_fin]: notgabtab[st].append(a)

    return notgabtab


def calc_h_of_triangle(a, b, c):
    # calc h of triangle
    # if we have triangle with vertices a, b, c
    # then we need to find h - which is start from c and is perpendicular to ab
    # to find it we will use formula:
    # (1) h=2*S/A  where s - area of triangle, A - length of side of triangle (ab in our case)
    # to find S we will use formula: (2) ((xb-xa)*(yc-ya)-(xc-xa)*(yb-ya))/2
    # then use (2) in (1) and have final formula:
    # (3) h = ((xb-xa)*(yc-ya)-(xc-xa)*(yb-ya))/ab
    # ! warning ! in south hemisphere we should use '-' before result,
    # as coordinates goes opposite direction than in north hemisphere

    x1, y1 = a[0], a[1]
    x2, y2 = b[0], b[1]
    x0, y0 = float(c[0]), float(c[1])
    len = round(sqrt((x2-x1)**2+(y2-y1)**2), 2)
    h = round((((x2-x1)*(y0-y1)-(x0-x1)*(y2-y1)) / len), 2)
    off = round(sqrt(((x0-x1)**2+(y0-y1)**2)-h**2), 2)
    return len, -h, off


def filltab(tab, str_coords):
    # now ngtab v2 has 10 columns:
    # (1) ts span name; (2) wire num; (3) 3d dist to ngab; (4,5,6) x,y,z of ngab point; (7) cline num;
    # (8) work id start span; (9) id span start; (10) id span end
    # here we add new columns: (11) span length; (12) station; (13) offset; (14) image name
    for span in range(len(tab)):
        # a = []    #span start coords (x, y)
        # b = []    #span end coords (x, y)
        # c = []    #ngab coords (x, y)
        for struct in range(len(str_coords)):
            if tab[span][7] == str_coords[struct][0]:
                a = str_coords[struct][1:3]
                b = str_coords[struct+1][1:3]
                c = tab[span][3:5]
                l, offs, station = calc_h_of_triangle(a, b, c)
                image_name = f'{tab[span][8]}_{tab[span][9]}.jpg'
                for a in [l, station, offs, image_name]: tab[span].append(a)

    return tab


s_coo = centerline(p_str)
ids = spec_id(spec)   # get ids
ng_tab = notgabread(p)   # get ngtab (v1)
ng_tab2 = idspannames(ids, ng_tab)    # add id names to ngtab (v2)
ng_tab3 = filltab(ng_tab2, s_coo)    # add calcs (v3)

for i in range(len(ng_tab3)):
    print(ng_tab2[i])








# TODO - формат и расчет таблицы негабаритов
# TODO - вывод таблицы негабаритов в xlsx
# TODO - интерфейс
# TODO - таблица под qgis - пролеты с негабаритами, негабаритные точки, длины пролетов
# TODO - добавить обрезку длинных пролетов
