# centroids of structures
# using lidar data of powerline structures to find their axes

# сделать:
# - варианты без точек - проверить
# - вынести функции - посмотреть что еще
# - сделать репорт с выводом на экран !!
# - вывод в DXF


import struct
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point, Polygon
import csv

# пути
p = Path(r'/524_wir_16_notime_nocolor.bin')
p_cgtw = Path(r'/tower331.pts')   # path to ctow
fin_cgt = Path(r'/cgtow_corr.txt')
fin_top = Path(r'/tops_corr.txt')


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


def file_write(path):
    # ну и сохранить в выходные файлы теперь
    with open(path, 'w', newline='') as the_file:
        points_writer = csv.writer(the_file, delimiter=' ')
        for tup in cgtow_corr:
            points_writer.writerow(tup)


def z_level(x, y, g_array, radius):
    s = Point(x, y)  # используем уточненную координату
    grd_cut2 = g_array[g_array.within(s.buffer(radius))]  # вырезаем поуже
    return np.mean(grd_cut2['z'])  # новый уровень земли


p_header, i_points = bin_reader(p)   # вызываем функцию чтения файла
print(p_header)

# импортные точки переводим в панду и удаляем ненужные колонки
p_points = pd.DataFrame(i_points, columns=p_header)
p_points = p_points[['x', 'y', 'z', 'class']]
del i_points, p_header   # удаляем, больше не нужно


# из общего массива точек извлекаем только нужные классы (землю и тела опор)
grd = p_points[p_points['class'] == grd_class][['x', 'y', 'z']]
tows = p_points[p_points['class'] == structure_points_class][['x', 'y', 'z']]
del p_points   # удаляем ненужное


# переводим панду в геопанду
grd_g = gpd.GeoDataFrame(grd, crs="EPSG:2193", geometry=gpd.points_from_xy(grd['x'], grd['y'], grd['z']))
tows_g = gpd.GeoDataFrame(tows, crs="EPSG:2193", geometry=gpd.points_from_xy(tows['x'], tows['y'], tows['z']))


# предварительные координаты опор в панду
c_tab = pd.read_csv(p_cgtw, sep='\s+', header=None, names=['id', 'x', 'y', 'z'])   # read to pandas

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
    tow_cut = tows_g[tows_g.within(tow_buf)]   # вырезаем то что попало в буфер
    grd_cut = grd_g[grd_g.within(tow_buf)]
    n_id = cgtw_g.loc[n, 'id']   # id initial
    n_x, n_y, n_z = (round(cgtw_g.loc[n, i]/100, 2) for i in ('x', 'y', 'z'))   # xyz initial

    # добавить проверку есть ли чтото в массивах
    if len(tow_cut) == 0 and len(grd_cut) == 0:
        # если не найдено точек опоры и земли оставляем исходные
        cgt = (n_id, n_z, n_y, n_z)
        top = cgt

    elif len(tow_cut) == 0 and len(grd_cut) != 0:
        # если точек от опоры нет, но есть земля - уточняем землю
        grd_lvl = z_level(n_x, n_y, grd_cut, buf_radius_2)
        cgt = (n_id, n_x, n_y, round(grd_lvl / 100, 2))
        top = cgt

    elif len(tow_cut) != 0:
        # если есть точки опоры
        if len(grd_cut) != 0:
            grd_lvl = np.mean(grd_cut['z'])   # средняя высота земли для расчета примерной высоты опоры
        else:
            grd_lvl = min(tow_cut['z'])   # если нет земли нижняя точка определяется по нижнему отражению опоры

        tow_top = max(tow_cut['z'])   # верхнее отражение от опоры (наивысшая точка)

        # начинаем с верхушки опоры
        up_lvl = (tow_top - grd_lvl) * ((100 - up_str) / 100) + grd_lvl
        tow_up = tow_cut[tow_cut['z'] > up_lvl]   # upper points
        # находим центр
        up_pol = Polygon(tow_up.iloc[i, [0, 1]] for i in range(len(tow_up)))   # переводим в полигон
        up_fig = up_pol.convex_hull.buffer(polybuff).centroid   # строим внешний контур, затем буфер вокруг него и центроид

        # работа с основанием опоры - в пределах верхушки + up_buf
        bot_lvl = (tow_top - grd_lvl) * (bot_str / 100) + grd_lvl   # высота части основания
        tow_bot = tow_cut[tow_cut['z'] < bot_lvl]   # вырезаем массив опоры у основания
        # находим центр
        bot_pol = Polygon(tow_bot.iloc[i, [0, 1]] for i in range(len(tow_bot)))   # переводим в полигон
        bot_fig = bot_pol.convex_hull.buffer(polybuff).centroid   # строим внешний контур и находим его центроид

        # теперь уточним высоту на земле, для этого возьмем радиус поуже
        if len(grd_cut) != 0:
            grd_lvl = z_level(bot_fig.x, bot_fig.y, grd_cut, buf_radius_2)

        # итоговая координата опоры на земле
        cgt = (n_id, round(bot_fig.x / 100, 2), round(bot_fig.y / 100, 2), round(grd_lvl / 100, 2))
        # итоговая координата опоры на верхушке
        top = (n_id, round(up_fig.x / 100, 2), round(up_fig.y / 100, 2), round(tow_top / 100, 2))

    else:
        # если ничего не понятно
        cgt = ('error', 0, 0, 0)
        top = cgt

    # теперь добавляем полученное в списки
    cgtow_corr.append(cgt)
    tower_tops.append(top)

file_write(fin_cgt)
file_write(fin_top)



####  общая схема и статус:
# - интерфейс - пути, задание параметров
# - выбор лас или бин
# - чтение данных
# - выборка только нужных классов
# - поопорный проход циклом
# - - для каждой опоры:
# - - вырезаем буфером землю и точки опоры
# - - проверяем есть ли что нибудь в массивах, если нет то прописываем сами координаты из входного файла
# - - для определения размера опоры находим предварительный уровень земли и верхнее отражение опоры
# - - отрезаем из массива опоры верхнюю часть (без Z)
# - - строим вокруг этих точек полигон, упрощаем его, строим вокруг буфер и находим от этого всего центроид
# - - тоже от нижней части опоры
# - - - можно попробовать вырезать низ в пределах верхней траверсы (когда она будет, пока не в этом алгоритме)
# - - вокруг нижней координаты вырезаем землю поуже и уточняем высоту
# - - сохраняем координаты верхушки и низа
# - - ++ добавить построение оси от верха до низа
# - после прохода по всем опорам экспорт в csv
# - ++ добавить экспорт осей в dxf (а может и центрлайна тоже)






