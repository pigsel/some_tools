# centroids of structures
# using lidar data of powerline structures to find their axes


import struct
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point, MultiPoint, LineString, MultiLineString
from shapely.ops import split
import csv

# пути
workdir = Path(r'D:\work\2022_makarov\training\ok')
p_bin = workdir / '645.bin'
p_cgtw = workdir / 'ctow.txt'  # path to ctow

resultdir = workdir / 'result'
if not resultdir.exists():
    resultdir.mkdir()

fin_cgt = resultdir / 'cgtow_corr.txt'    # final file
fin_top = resultdir / 'tops_corr.txt'    # final file
repr_path = resultdir / 'cst_report.txt'    # final report
p_dxf = resultdir / 'cline_corr.dxf'

tempdir = workdir / 'temp'
if not tempdir.exists():
    tempdir.mkdir()


# переменные
grd_class = 2   # номер класса с точками земли
structure_points_class = 203   # номер класса с ТЛО от опор
buf_radius = 15   # первоначальный радиус отбора точек опор и земли
buf_radius_2 = 2   # радиус отбора точек земли для финального уточнения высоты
polybuff = 1   # буфер вокруг полигона при поиске центроида
bot_str = 10    # процент от высоты опоры снизу для определения центра
up_str = 10    # процент от высоты опоры сверху для определения центра
rprt = []   # репорт


def bin_reader(p):
    # функция чтения бинфайлов terrascan - 8 или 16 bit
    bin_data = p.read_bytes()

    # HEADER
    bin_header = struct.unpack('<3i4sli3d2i', bin_data[0:56])
    # hdr_size = bin_header[0]   # header size
    # hdr_version = bin_header[1]   # Version 20020715, 20010712, 20010129 or 970404
    # pnt_cnt = bin_header[4]   # Number of points stored
    # bin_units = bin_header[5]   # Units per meter = subpermast * uorpersub
    # bin_time = bin_header[9]   # 32 bit integer time stamps appended to points
    # bin_color = bin_header[10]   # Color values appended to points
    # head_ind = (bin_header[1], bin_header[9], bin_header[10])  # to choose calc
    print(bin_header)

    # out_header = ['x', 'y', 'z', 'class', 'echo', 'run_f1', 'run_f2', 'flightline', 'intensity', 'time', 'color']

    # 16 bit
    if bin_header[1] == 20020715:
        if bin_header[9] != 0 and bin_header[10] == 0:
            out_header = ['x', 'y', 'z', 'class', 'echo', 'run_f1', 'run_f2', 'flightline', 'intensity', 'time']
            points = tuple(struct.iter_unpack('<3L4B2HI', bin_data[56:]))  # (24, '3l4b2HI', 10)

        elif bin_header[9] == 0 and bin_header[10] != 0:
            out_header = ['x', 'y', 'z', 'class', 'echo', 'run_f1', 'run_f2', 'flightline', 'intensity', 'color']
            points = tuple(struct.iter_unpack('<3L4B2HI', bin_data[56:]))  # (24, '3l4b2HI', 10)

        elif bin_header[9] == 0 and bin_header[10] == 0:
            out_header = ['x', 'y', 'z', 'class', 'echo', 'run_f1', 'run_f2', 'flightline', 'intensity']
            points = tuple(struct.iter_unpack('<3L4B2H', bin_data[56:]))  # (20, '3l4b2H', 9)

        elif bin_header[9] != 0 and bin_header[10] != 0:
            out_header = ['x', 'y', 'z', 'class', 'echo', 'run_f1', 'run_f2', 'flightline', 'intensity', 'time',
                          'color']
            points = tuple(struct.iter_unpack('<3L4B2H2I', bin_data[56:]))  # (28, '3l4b2H2I', 11)


    # 8 bit
    elif bin_header[1] == 20010712:
        if bin_header[9] != 0 and bin_header[10] == 0:
            out_header = ['class', 'flight', 'intens_echo', 'x', 'y', 'z', 'time']
            points = tuple(struct.iter_unpack('<2BH3LI', bin_data[56:]))

        elif bin_header[9] == 0 and bin_header[10] == 0:
            out_header = ['class', 'flight', 'intens_echo', 'x', 'y', 'z']
            points = tuple(struct.iter_unpack('<2BH3L', bin_data[56:]))

        elif bin_header[9] != 0 and bin_header[10] != 0:
            out_header = ['class', 'flight', 'intens_echo', 'x', 'y', 'z', 'time', 'color']
            points = tuple(struct.iter_unpack('<2BH3L2I', bin_data[56:]))  # (24, '2bH3l2I', 8)

        elif bin_header[9] == 0 and bin_header[10] != 0:
            out_header = ['class', 'flight', 'intens_echo', 'x', 'y', 'z', 'color']
            points = tuple(struct.iter_unpack('<2BH3LI', bin_data[56:]))  # (20, '2bH3lI', 7)

    else:
        out_header = ['неверный формат файла']
        points = ['ищи ошибку']

    return out_header, points


def struct_boxes(cgtw_g, buf_kor):
    # для коридоров достаточно построить 2д линии
    coo_2d = []
    line_n = 1
    spam = []
    for i in range(1, len(cgtw_g) + 1):
        if cgtw_g.loc[i, 'c_line'] == line_n:
            spam.append((cgtw_g.loc[i].x, cgtw_g.loc[i].y))
            if i == len(cgtw_g): coo_2d.append(tuple(spam))
        else:
            coo_2d.append(tuple(spam))
            spam = []
            line_n = cgtw_g.loc[i, 'c_line']
            spam.append((cgtw_g.loc[i].x, cgtw_g.loc[i].y))

    m_lines_2d = MultiLineString(coo_2d)    # переводим в мультилинии
    report('построены полилинии для коридоров', rprt)

    # строим коридоры вокруг центрлайнов и нарезаем их
    mid_points = []   # цетры пролетов
    str_boxes = []   # нарезанные боксы
    for line in m_lines_2d.geoms:
        kor_spam = line.buffer(buf_kor)
        for i in range(len(line.coords) - 1):
            mp = LineString([line.coords[i], line.coords[i + 1]]).interpolate(0.5, normalized=True)  # mid point
            mid_points.append(mp)

            spam = LineString([line.coords[i], mp])  # line from str to mid
            left = spam.parallel_offset((buf_kor+3), 'left')  # left parallel line
            right = spam.parallel_offset((buf_kor+3), 'right')  # right parallel line
            xline = LineString([left.boundary.geoms[1], right.boundary.geoms[0]])  # x-line on mid point

            cut = split(kor_spam, xline)   # режем коридор по x-line на две части
            #print(i, len(cut))
            if Point(line.coords[i]).within(cut.geoms[0]):    # проверяем какой из коридоров нам нужен
                str_boxes.append(cut.geoms[0])    # наш (отрезок) коридор добавляем в список
                kor_spam = cut.geoms[1]    # переприсваиваем оставшуюся большую часть
            else:
                str_boxes.append(cut.geoms[1])
                kor_spam = cut.geoms[0]

        str_boxes.append(kor_spam)   # последний кусок добавляем отдельно

    report('построены коридоры, проводим слияние в узловых точках', rprt)
    uniq_str = list(set(cgtw_g.id))   # предварительно уникальные номера опор (без повторений)
    junktion_points = []  # повторяющиеся (узловые) опоры

    for str in uniq_str:
        if list(cgtw_g.id).count(str) > 1:   # если опор с одним id номером больше одной
            junktion_points.append(str)

    # делаем проверку действительно ли эти опоры имеют одинаковые координаты и если нет, удаляем из списка
    for jp in junktion_points:
        jp_p = cgtw_g[cgtw_g['id'] == jp]
        spam = jp_p.iloc[0].geometry
        for a in range(len(jp_p)):
            if jp_p.iloc[a].geometry != spam:
                junktion_points.remove(jp)
                uniq_str.append(jp)
                #print('перенес одного.. ')
    report('проверка уникальности узловых опор', rprt)

    # replace boxes / объединяем накладывающиеся боксы в один
    for pnt in junktion_points:
        point = cgtw_g[cgtw_g['id'] == pnt].iloc[0].geometry
        bb = 0
        for box in str_boxes:   # для каждого бокса проверяем попадает ли туда узловая опора
            if point.within(box):
                if bb == 0:
                    bb = box
                else:
                    bb = bb.union(box)   # объединяем
                str_boxes.remove(box)   # старый удаляем
        if bb != 0:
            str_boxes.append(bb)   # затем добавляем новый

    report('коридоры объединены', rprt)
    return str_boxes


def file_write(path, points_arr):
    # сохранить в текстовые файлы с разделителем пробелом
    with open(path, 'w', newline='') as the_file:
        points_writer = csv.writer(the_file, delimiter=' ')
        if type(points_arr) == MultiPoint:
            for po in points_arr:
                p_coo = (po.x, po.y, po.z)
                points_writer.writerow(p_coo)
        else:
            for tup in points_arr:
                points_writer.writerow(tup)


def xyz_read(path):
    # read xyz arrays from files
    with open(path, newline='') as xyz_file:
        spamlist = []
        spamreader = csv.reader(xyz_file, delimiter=' ', quoting=csv.QUOTE_NONNUMERIC, skipinitialspace=True)
        for row in spamreader:
            spamlist.append(row)
        #spamlist = MultiPoint(spamlist)   # убираю - пусть останется просто лист

    return spamlist


def z_level_gpd(x, y, g_array, radius):
    # for geopandas array
    s = Point(x, y)  # используем уточненную координату
    grd_cut2 = g_array[g_array.within(s.buffer(radius))]  # вырезаем поуже
    return np.mean(grd_cut2['z'])  # новый уровень земли


def z_level_shp(x, y, g_array, radius):
    # for shapely array
    g_array = MultiPoint(g_array)   # to shapely
    s = Point(x, y)  # используем уточненную координату
    grd_cut2 = g_array.intersection(s.buffer(radius))   # вырезаем поуже

    if type(grd_cut2) == Point:
        return grd_cut2.z

    elif len(grd_cut2.geoms) > 0:
        aa = []    # переводим назад в простой массив (new shapely does not work well)
        for i in grd_cut2.geoms:
            aa.append(list(i.coords)[0])

        return np.mean(aa, axis=0)[2]  # новый уровень земли

    else:
        report('ошибка определения высоты опоры, приравниваем к 0', rprt)
        return 0


def centerline(cgt_p):
    c_lines = []  # list of structures
    num_of_clines = 1  # number of c-line
    str_index = 1  # index of structure
    with open(p_cgtw) as ffile:
        for line in ffile:
            stroka = line.strip('\n').split()
            if len(stroka) == 4:
                # ctow file should contain id, x, y, z in each row
                # to c-lines list we add to each row index of stucture and number of c-line
                c_lines.append((str_index, num_of_clines, stroka[0], float(stroka[1]), float(stroka[2]), float(stroka[3])))
                str_index += 1  # index for next structure
            elif len(stroka) == 0:
                num_of_clines += 1  # blank row means next c-line follow
            else:
                print('ctow file error')

    report(f'в объекте {num_of_clines} центрлайн, загружено опор: {len(c_lines)}', rprt)
    #print(c_lines)

    # загружаем в панду (чтобы была возможность поработать со столбцами)
    cgtw_g = pd.DataFrame(c_lines, columns=['index', 'c_line', 'id', 'x', 'y', 'z']).set_index('index')

    # ну и в геопанду это всё
    cgtw_g = gpd.GeoDataFrame(cgtw_g, crs="EPSG:2193", geometry=gpd.points_from_xy(cgtw_g['x'], cgtw_g['y'], cgtw_g['z']))
    report('геопривязка опор завершена', rprt)
    return cgtw_g


def points_cut(ini_points, ini_head, grd_cls, str_cls):
    # collect only grd and structure xyz and /100 as in bin file coords *100
    grd_p = []
    str_p = []

    for i in range(len(ini_points)):
        po = list(ini_points[i])   # each row in i_points (all values)
        if po[ini_head.index('class')] == grd_cls:
            grd_p.append(list(po[ini_head.index(c)]/100 for c in ['x', 'y', 'z']))   # add grd points
        elif po[ini_head.index('class')] == str_cls:
            str_p.append(list(po[ini_head.index(c)]/100 for c in ['x', 'y', 'z']))   # add structure points

    report(f'загружено точек опор: {len(str_p)}, земли: {len(grd_p)}', rprt)

    # str_p = MultiPoint(str_p)   # делаем массивы shapely (multipoints - z points) / зачем? - для определения bounds
    # grd_p = MultiPoint(grd_p)
    return str_p, grd_p


def isinbounds(x, y, bounds):
    if bounds[2] >= x >= bounds[0] and bounds[3] >= y >= bounds[1]:
        return True
    else:
        return False


def cut_by_dist(arr, x, y, buf):
    spamlist = []
    buf = buf**2
    for row in arr:
        dist = (x - row[0]) ** 2 + (y - row[1]) ** 2
        if dist < buf:
            spamlist.append(row)
    return spamlist


def cutbyboxes2(cgtw_g, str_bounds, str_boxes, str_p, grd_p, buf_radius):
    # добавляем в таблицу опор колонку havepoints где будем отмечать есть точки или нет
    cgtw_g['havepoints'] = 0
    grd_to_box = []
    str_to_box = []
    # дальше проверяем есть ли точки на эту опору и проставляем метки
    for n in range(len(cgtw_g)):
        idx = cgtw_g.iloc[n].name   # find index and work with it
        if isinbounds(cgtw_g.loc[idx, 'x'], cgtw_g.loc[idx, 'y'], str_bounds):
            cgtw_g.loc[idx, 'havepoints'] = 1
            for box in str_boxes:
                if cgtw_g.loc[idx].geometry.within(box):
                    str_f_path = tempdir / str(f"{idx}_{cgtw_g.loc[idx, 'id']}_str.xyz")
                    grd_f_path = tempdir / str(f"{idx}_{cgtw_g.loc[idx, 'id']}_grd.xyz")
                    if not str_f_path.exists():

                        str_to_box = cut_by_dist(str_p, cgtw_g.loc[idx, 'x'], cgtw_g.loc[idx, 'y'], buf_radius)  # вырезаем
                        grd_to_box = cut_by_dist(grd_p, cgtw_g.loc[idx, 'x'], cgtw_g.loc[idx, 'y'], buf_radius)
                        file_write(str_f_path, str_to_box)
                        file_write(grd_f_path, grd_to_box)
                        report(f'ТЛО для {idx} записаны в отдельные файлы', rprt)
    cgtw_g.to_csv('cgtw.txt', sep='\t')
    return cgtw_g


def dub_del(li):
    # python has 'set' function to delete dubs, but it make list unsort
    new_li = []
    for x in range(len(li)):
        if li[x] not in new_li:
            new_li.append(li[x])
    return new_li


def find_center(cgtw_g, buf_radius_2, polybuff):
    # дальше цикл прохода по каждой опоре и уточнение ее центра
    cgtow_corr = []  # обновленные координаты опор середина
    tower_tops = []  # центры верхушек опор середина

    # добавляем нулевые колонки, затем туда вставим уточненные координаты (для первого и второго методов)
    cgtw_g['x1'] = cgtw_g['y1'] = cgtw_g['z1'] = 0
    cgtw_g['x1_t'] = cgtw_g['y1_t'] = cgtw_g['z1_t'] = 0
    cgtw_g['angle'] = 0


    for n in range(len(cgtw_g)):
        idx = cgtw_g.iloc[n].name  # find index and work with index
        # parse cgtw
        n_id = cgtw_g.loc[idx, 'id']  # id initial
        n_x, n_y, n_z = (round(cgtw_g.loc[idx, i], 2) for i in ('x', 'y', 'z'))  # xyz initial
        # cut from boxes
        if cgtw_g.loc[idx, 'havepoints'] == 1:
            # переделываю эту часть в простой массив, вместо MultiPoint
            tow_cut = xyz_read(tempdir / str(f"{idx}_{cgtw_g.loc[idx, 'id']}_str.xyz"))
            grd_cut = xyz_read(tempdir / str(f"{idx}_{cgtw_g.loc[idx, 'id']}_grd.xyz"))
        else:
            tow_cut = grd_cut = []  # пустой лист если опоры вне области точек

        if len(tow_cut) == 0 and len(grd_cut) == 0:
            # если не найдено точек опоры и земли оставляем исходные
            cgt = (n_id, n_x, n_y, n_z)
            top = cgt_2 = top_2 = cgt
            report(f'опора: {n_id} - оставлены исходные координаты (ТЛО не найдены)', rprt)

        elif len(tow_cut) == 0 and len(grd_cut) != 0:
            # если точек от опоры нет, но есть земля - уточняем землю
            grd_lvl = z_level_shp(n_x, n_y, grd_cut, buf_radius_2)
            cgt = (n_id, n_x, n_y, round(grd_lvl, 2))
            top = cgt_2 = top_2 = cgt
            report(f'опора: {n_id} - уточнена только высота (ТЛО опоры не найдены)', rprt)

        elif len(tow_cut) != 0:
            # если есть точки опоры
            if len(grd_cut) != 0:
                grd_lvl = np.mean(grd_cut, axis=0)[2]  # средняя высота земли для расчета примерной высоты опоры
            else:
                grd_lvl = np.min(tow_cut, axis=0)[2]  # если нет земли нижняя точка определяется по нижнему отражению опоры
                report(f'опора: {n_id} - нет ТЛО земли, высота определена по нижнему отражению опоры', rprt)

            # верхнее отражение от опоры (наивысшая точка)
            tow_top = np.max(tow_cut, axis=0)[2]
            # нижнее отражение от опоры (нижняя точка) + 1 метр чтобы исключить фундамент/мусор
            tow_low = (np.min(tow_cut, axis=0)[2])+1

            # начинаем с верхушки опоры
            up_lvl = tow_top - 1   # try this
            #up_lvl = (tow_top - grd_lvl) * ((100 - up_str) / 100) + grd_lvl
            tow_up = []
            for i in range(len(tow_cut)):
                if tow_cut[i][2] > up_lvl:
                    tow_up.append(tow_cut[i])  # upper points
            tow_up = MultiPoint(tow_up)
            # находим центр
            up_fig = tow_up.convex_hull.buffer(polybuff).centroid  # центр буфера вокруг описывающего полигона
            # method 2
            #up_fig = tow_up.minimum_rotated_rectangle.centroid  # центр минимального описывающего прямоугольника

            # работа с основанием опоры - в пределах верхушки + up_buf -2m
            bot_lvl = (tow_top - tow_low) * (bot_str / 100) + tow_low  # высота части основания от нижнего отражения
            tow_bot = []
            for i in range(len(tow_cut)):
                if tow_low+2 < tow_cut[i][2] < bot_lvl:
                    tow_bot.append(tow_cut[i])  # upper points
            tow_bot = MultiPoint(tow_bot)

            # находим центр
            bot_fig = tow_bot.convex_hull.buffer(polybuff).centroid  # центр буфера вокруг описывающего полигона
            # method 2
            # bot_fig_2 = tow_bot.minimum_rotated_rectangle.centroid  # центр минимального описывающего прямоугольника

            # теперь уточним высоту на земле, для этого возьмем радиус поуже
            if len(grd_cut) != 0:
                grd_lvl_corr = z_level_shp(bot_fig.x, bot_fig.y, grd_cut, buf_radius_2)
                if grd_lvl_corr != 0:
                    grd_lvl = grd_lvl_corr

            # итоговые координаты
            cgt = (n_id, round(bot_fig.x, 2), round(bot_fig.y, 2), round(grd_lvl, 2))
            top = (n_id, round(up_fig.x, 2), round(up_fig.y, 2), round(tow_top, 2))
            # второй метод
            # cgt_2 = (n_id, round(bot_fig_2.x, 2), round(bot_fig_2.y, 2), round(grd_lvl, 2))
            # top_2 = (n_id, round(up_fig_2.x, 2), round(up_fig_2.y, 2), round(tow_top, 2))

            report(f'опора: {n_id} - координаты уточнены', rprt)

        else:
            # если ничего не понятно
            cgt = ('error', 0, 0, 0)
            top = top_2 = cgt_2 = cgt
            report(f'опора: {n_id} - неизвестная ошибка', rprt)

        # теперь добавляем полученное в списки
        cgtow_corr.append(cgt)
        tower_tops.append(top)

        # теперь добавить всё это в cgtw_g
        for numb, name in enumerate(['x1', 'y1', 'z1']):
            cgtw_g.loc[idx, name] = cgt[numb+1]
        for numb, name in enumerate(['x1_t', 'y1_t', 'z1_t']):
            cgtw_g.loc[idx, name] = top[numb+1]

    cgtw_g.to_excel(resultdir / "cgtw_output.xlsx")  # save cgtw_g to xls

    # возвращаем листы без дубликатов
    return dub_del(cgtow_corr), dub_del(tower_tops), cgtw_g


def report(text, rep):
    print(text)
    rep.append(text)
    with open(repr_path, 'w', newline='') as rep_file:
        csv.writer(rep_file, delimiter='\n').writerow(rprt)


# creating DXF
def vert_axes(cgtw_g):
    # values
    layername = 'Vert'
    color = 0
    text = ""   # future part of DXF with vert axes
    structures = []   # list of str to exclude dubs

    for n in range(len(cgtw_g)):
        idx = cgtw_g.iloc[n].name   # find index and work with it

        spam = cgtw_g.loc[idx, 'id']   # structure ID
        # check if it not in list
        if spam not in structures:
            structures.append(spam)

            # add header
            text += f'0\nLINE\n 8\n{layername}\n 62\n     {color}\n'

            # add bottom coords
            text += f" 10\n{cgtw_g.loc[idx, 'x1']}\n 20\n{cgtw_g.loc[idx, 'y1']}\n 30\n{cgtw_g.loc[idx, 'z1']}\n"

            # add top coords
            text += f" 11\n{cgtw_g.loc[idx, 'x1_t']}\n 21\n{cgtw_g.loc[idx, 'y1_t']}\n 31\n{cgtw_g.loc[idx, 'z1_t']}\n"

    return text


def polylines(cgtw_g):
    "создает часть файла с полилиниями (ценртлайн)"

    # переменные
    layername = 'Centerline'
    color = 2
    closed = 136  # для polyline 136 = не замкнуто, 9 = замкнуто
    line_num = 1
    # header
    text = f'  0\nPOLYLINE\n 8\n{layername}\n 62\n     {color}\n 70\n   {closed}\n'

    for n in range(len(cgtw_g)):
        idx = cgtw_g.iloc[n].name   # find index and work with it

        if line_num == cgtw_g.loc[idx, 'c_line']:
            # write coord for each vertex for same line
            text += f"  0\nVERTEX\n 10\n{cgtw_g.loc[idx, 'x1']}\n 20\n{cgtw_g.loc[idx, 'y1']}\n 30\n{cgtw_g.loc[idx, 'z1']}\n"

        else:
            # close existing line
            text += '  0\nSEQEND\n'
            # if we have another line - write also header and first vertex
            line_num = cgtw_g.loc[idx, 'c_line']   # give line new number
            # header again for new line
            text += f'  0\nPOLYLINE\n 8\n{layername}\n 62\n     {color}\n 70\n   {closed}\n'
            # first vertex
            text += f"  0\nVERTEX\n 10\n{cgtw_g.loc[idx, 'x1']}\n 20\n{cgtw_g.loc[idx, 'y1']}\n 30\n{cgtw_g.loc[idx, 'z1']}\n"

    # close last line as it is last vertex
    text += '  0\nSEQEND\n'

    return text


################################################################
#  начало расчетной части  -  собираем функции

p_header, i_points = bin_reader(p_bin)   # вызываем функцию чтения файла и получаем массив

# вырезаем массивы точек опор и земли
str_p, grd_p = points_cut(i_points, p_header, grd_class, structure_points_class)

del i_points  # удаляем т.к. не нужно больше

cgtw_g = centerline(p_cgtw)   # загружаем координаты опор

# x-y bounding box is a (minx, miny, maxx, maxy) tuple / shapely
str_bounds = MultiPoint(str_p).bounds   # границы загружаемых точек

# ищем коридоры
str_boxes = struct_boxes(cgtw_g, buf_radius)

# cut
cgtw_g = cutbyboxes2(cgtw_g, str_bounds, str_boxes, str_p, grd_p, buf_radius)

# поиск центров
cgtow_corr, tower_tops, cgtw_g = find_center(cgtw_g, buf_radius_2, polybuff)

# записываем в файлы
file_write(fin_cgt, cgtow_corr)
file_write(fin_top, tower_tops)
report('записаны выходные файлы: cgtow_corr.txt, tops_corr.txt', rprt)

# creating DXF
p_dxf.write_text('  0\nSECTION\n  2\nENTITIES\n' + vert_axes(cgtw_g) + polylines(cgtw_g) + '  0\nENDSEC\n  0\nEOF')

input('расчет завершен, нажмите Enter для выхода')
