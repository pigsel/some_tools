# centroids of structures
# using lidar data of powerline structures to find their axes

# TODO - 2 вынести функции - посмотреть что еще
# TODO - 3 вывод в DXF
# TODO - 4 интерфейс !
# TODO - 1 добавить общий контур массивов чтобы не перебирать точки


import struct
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point, MultiPoint, Polygon
import csv

# пути
p = Path(r'D:\python\some_tools\centrostruct\524_wir_16_notime_nocolor.bin')
p_cgtw = Path(r'D:\python\some_tools\centrostruct\tower331.pts')   # path to ctow
fin_cgt = Path(r'D:\python\some_tools\centrostruct\cgtow_corr.txt')
fin_top = Path(r'D:\python\some_tools\centrostruct\tops_corr.txt')
fin_cgt_2 = Path(r'D:\python\some_tools\centrostruct\cgtow_corr_m2.txt')
fin_top_2 = Path(r'D:\python\some_tools\centrostruct\tops_corr_m2.txt')
repr_path = Path(r'D:\python\some_tools\centrostruct\cst_report.txt')

# переменные
grd_class = 2   # номер класса с точками земли
structure_points_class = 203   # номер класса с ТЛО от опор
buf_radius = 1500   # первоначальный радиус отбора точек опор и земли (метры умноженные на 100)
buf_radius_2 = 200   # радиус отбора точек земли для финального уточнения высоты (метры умноженные на 100)
polybuff = 200   # буфер вокруг полигона при поиске центроида
bot_str = 30    # процент от высоты опоры снизу для определения центра
up_str = 10    # процент от высоты опоры сверху для определения центра
cgtow_corr = []   # обновленные координаты опор середина
tower_tops = []   # центры верхушек опор середина
cgtow_corr_2 = []   # обновленные координаты опор середина (метод 2)
tower_tops_2 = []   # центры верхушек опор середина (метод 2)
rprt = []   # репорт


def bin_reader(p):
    # функция чтения бинфайлов terrascan - 8 или 16 bit
    bin_data = p.read_bytes()

    # HEADER
    bin_header = struct.unpack('3i4sli3d2i', bin_data[0:56])
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
            points = tuple(struct.iter_unpack('3L4B2HI', bin_data[56:]))  # (24, '3l4b2HI', 10)

        elif bin_header[9] == 0 and bin_header[10] != 0:
            out_header = ['x', 'y', 'z', 'class', 'echo', 'run_f1', 'run_f2', 'flightline', 'intensity', 'color']
            points = tuple(struct.iter_unpack('3L4B2HI', bin_data[56:]))  # (24, '3l4b2HI', 10)

        elif bin_header[9] == 0 and bin_header[10] == 0:
            out_header = ['x', 'y', 'z', 'class', 'echo', 'run_f1', 'run_f2', 'flightline', 'intensity']
            points = tuple(struct.iter_unpack('3L4B2H', bin_data[56:]))  # (20, '3l4b2H', 9)

        elif bin_header[9] != 0 and bin_header[10] != 0:
            out_header = ['x', 'y', 'z', 'class', 'echo', 'run_f1', 'run_f2', 'flightline', 'intensity', 'time',
                          'color']
            points = tuple(struct.iter_unpack('3L4B2H2I', bin_data[56:]))  # (28, '3l4b2H2I', 11)


    # 8 bit
    elif bin_header[1] == 20010712:
        if bin_header[9] != 0 and bin_header[10] == 0:
            out_header = ['class', 'flight', 'intens_echo', 'x', 'y', 'z', 'time']
            points = tuple(struct.iter_unpack('2BH3LI', bin_data[56:]))

        elif bin_header[9] == 0 and bin_header[10] == 0:
            out_header = ['class', 'flight', 'intens_echo', 'x', 'y', 'z']
            points = tuple(struct.iter_unpack('2BH3L', bin_data[56:]))

        elif bin_header[9] != 0 and bin_header[10] != 0:
            out_header = ['class', 'flight', 'intens_echo', 'x', 'y', 'z', 'time', 'color']
            points = tuple(struct.iter_unpack('2BH3L2I', bin_data[56:]))  # (24, '2bH3l2I', 8)

        elif bin_header[9] == 0 and bin_header[10] != 0:
            out_header = ['class', 'flight', 'intens_echo', 'x', 'y', 'z', 'color']
            points = tuple(struct.iter_unpack('2BH3LI', bin_data[56:]))  # (20, '2bH3lI', 7)

    else:
        out_header = ['неверный формат файла']
        points = ['ищи ошибку']

    return out_header, points


def file_write(path, points_arr):
    # сохранить в текстовые файлы с разделителем пробелом
    with open(path, 'w', newline='') as the_file:
        points_writer = csv.writer(the_file, delimiter=' ')
        for tup in points_arr:
            points_writer.writerow(tup)


def z_level_gpd(x, y, g_array, radius):
    # for geopandas array
    s = Point(x, y)  # используем уточненную координату
    grd_cut2 = g_array[g_array.within(s.buffer(radius))]  # вырезаем поуже
    return np.mean(grd_cut2['z'])  # новый уровень земли


def z_level_shp(x, y, g_array, radius):
    # for shapely array
    s = Point(x, y)  # используем уточненную координату
    grd_cut2 = g_array.intersection(s.buffer(radius))   # вырезаем поуже
    return np.mean(grd_cut2, axis=0)[2]  # новый уровень земли


def report(text, rep):
    print(text)
    rep.append(text)


report('сначала загружаем бин файл', rprt)

p_header, i_points = bin_reader(p)   # вызываем функцию чтения файла

# new version (get rid of pandas)
grd_p = []
str_p = []

for i in range(len(i_points)):
    po = list(i_points[i])   # each point in i_points (all values)
    if po[p_header.index('class')] == grd_class:
        grd_p.append(list(po[p_header.index(z)] for z in ['x', 'y', 'z']))   # add grd points
    elif po[p_header.index('class')] == structure_points_class:
        str_p.append(list(po[p_header.index(z)] for z in ['x', 'y', 'z']))   # add structure points

report(f'загружено точек опор: {len(grd_p)}, земли: {len(str_p)}', rprt)

del i_points    # удаляем т.к. не нужно больше
str_p = MultiPoint(str_p)   # делаем массивы shapely (multipoints - z points)
grd_p = MultiPoint(grd_p)

# переводим панду в геопанду
# grd_g = gpd.GeoDataFrame(grd, crs="EPSG:2193", geometry=gpd.points_from_xy(grd['x'], grd['y'], grd['z']))
# tows_g = gpd.GeoDataFrame(tows, crs="EPSG:2193", geometry=gpd.points_from_xy(tows['x'], tows['y'], tows['z']))
# report('произведена геопривязка массивов', rprt)

# предварительные координаты опор в панду
c_tab = pd.read_csv(p_cgtw, sep='\s+', header=None, names=['id', 'x', 'y', 'z'])   # read to pandas
report(f'загружено исходных координат опор: {len(c_tab)}', rprt)

# теперь умножаем координаты опор на 100
# т.к. в бинах точки умножены на 100, умножим и тут для простоты
# чтобы не делить все массивы - так быстрее
for i in ['x', 'y', 'z']:
    c_tab[i] = c_tab[i]*100

# ну и в геопанду это всё
cgtw_g = gpd.GeoDataFrame(c_tab, crs="EPSG:2193", geometry=gpd.points_from_xy(c_tab['x'], c_tab['y'], c_tab['z']))

# дальше цикл прохода по каждой опоре и уточнение ее центра
for n in range(len(cgtw_g)):
    tow_buf = cgtw_g.loc[n, 'geometry'].buffer(buf_radius)   # делаем буфер
    tow_cut = str_p.intersection(tow_buf)   # вырезаем то что попало в буфер
    grd_cut = grd_p.intersection(tow_buf)
    n_id = cgtw_g.loc[n, 'id']   # id initial
    n_x, n_y, n_z = (round(cgtw_g.loc[n, i]/100, 2) for i in ('x', 'y', 'z'))   # xyz initial

    # добавить проверку есть ли чтото в массивах
    if len(tow_cut) == 0 and len(grd_cut) == 0:
        # если не найдено точек опоры и земли оставляем исходные
        cgt = (n_id, n_x, n_y, n_z)
        top = cgt_2 = top_2 = cgt
        report(f'опора: {n_id} - оставлены исходные координаты (ТЛО не найдены)', rprt)

    elif len(tow_cut) == 0 and len(grd_cut) != 0:
        # если точек от опоры нет, но есть земля - уточняем землю
        grd_lvl = z_level_shp(n_x, n_y, grd_cut, buf_radius_2)
        cgt = (n_id, n_x, n_y, round(grd_lvl / 100, 2))
        top = cgt_2 = top_2 = cgt
        report(f'опора: {n_id} - уточнена только высота (ТЛО опоры не найдены)', rprt)

    elif len(tow_cut) != 0:
        # если есть точки опоры
        if len(grd_cut) != 0:
            grd_lvl = np.mean(grd_cut, axis=0)[2]   # средняя высота земли для расчета примерной высоты опоры
        else:
            grd_lvl = np.min(tow_cut, axis=0)[2]   # если нет земли нижняя точка определяется по нижнему отражению опоры
            report(f'опора: {n_id} - нет ТЛО земли, высота определена по нижнему отражению опоры', rprt)

        tow_top = np.max(tow_cut, axis=0)[2]   # верхнее отражение от опоры (наивысшая точка)


        # начинаем с верхушки опоры
        up_lvl = (tow_top - grd_lvl) * ((100 - up_str) / 100) + grd_lvl
        tow_up = []
        for i in range(len(tow_cut)):
            if tow_cut[i].z > up_lvl:
                tow_up.append(tow_cut[i])   # upper points
        tow_up = MultiPoint(tow_up)
        # находим центр
        up_fig = tow_up.convex_hull.buffer(polybuff).centroid   # центр буфера вокруг описывающего полигона
        # method 2
        up_fig_2 = tow_up.minimum_rotated_rectangle.centroid   # центр минимального описывающего прямоугольника

        # работа с основанием опоры - в пределах верхушки + up_buf
        bot_lvl = (tow_top - grd_lvl) * (bot_str / 100) + grd_lvl   # высота части основания
        tow_bot = []
        for i in range(len(tow_cut)):
            if tow_cut[i].z < bot_lvl:
                tow_bot.append(tow_cut[i])   # upper points
        tow_bot = MultiPoint(tow_bot)
        # находим центр
        bot_fig = tow_bot.convex_hull.buffer(polybuff).centroid   # центр буфера вокруг описывающего полигона
        # method 2
        bot_fig_2 = tow_bot.minimum_rotated_rectangle.centroid   # центр минимального описывающего прямоугольника

        # теперь уточним высоту на земле, для этого возьмем радиус поуже
        if len(grd_cut) != 0:
            grd_lvl = z_level_shp(bot_fig.x, bot_fig.y, grd_cut, buf_radius_2)

        # итоговые координаты
        cgt = (n_id, round(bot_fig.x / 100, 2), round(bot_fig.y / 100, 2), round(grd_lvl / 100, 2))
        top = (n_id, round(up_fig.x / 100, 2), round(up_fig.y / 100, 2), round(tow_top / 100, 2))
        # второй метод
        cgt_2 = (n_id, round(bot_fig_2.x / 100, 2), round(bot_fig_2.y / 100, 2), round(grd_lvl / 100, 2))
        top_2 = (n_id, round(up_fig_2.x / 100, 2), round(up_fig_2.y / 100, 2), round(tow_top / 100, 2))

        report(f'опора: {n_id} - координаты уточнены', rprt)

        # metod 2

    else:
        # если ничего не понятно
        cgt = ('error', 0, 0, 0)
        top = top_2 = cgt_2 = cgt
        report(f'опора: {n_id} - неизвестная ошибка', rprt)

    # теперь добавляем полученное в списки
    cgtow_corr.append(cgt)
    tower_tops.append(top)
    cgtow_corr_2.append(cgt_2)
    tower_tops_2.append(top_2)


file_write(fin_cgt, cgtow_corr)
file_write(fin_top, tower_tops)
file_write(fin_cgt_2, cgtow_corr_2)
file_write(fin_top_2, tower_tops_2)
report('записаны выходные файлы: cgtow_corr.txt, tops_corr.txt', rprt)

#  сохраняем репорт на последок
with open(repr_path, 'w', newline='') as rep_file:
    csv.writer(rep_file, delimiter='\n').writerow(rprt)

input('расчет завершен, нажмите Enter для выхода')
