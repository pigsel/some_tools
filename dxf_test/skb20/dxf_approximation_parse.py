# read dxf approx, find mid points and calc distances in between
# python 3.9
# author Igor Bertyaev

# ! вимание - программа работает только с одной цепью, в расчетной директории допустимо только три файла
# ! имя dxf  файла должно кончаться подчеркиванием и номером фазы *_1a.dxf


from pathlib import Path
import csv
import pandas as pd
# import openpyxl


# interface
# print('программа найдет центральные точки аппроксимаций')
# print('и посчитает расстояния между ними')
# print('! внимание - пока программа работает только с одной цепью')
# print('\nпожалуйста создайте директорию в которой будут:')
# print('- файлы аппроксимаций в формате *_1a.dxf (3 шт)')
# print('- текстовый файл координат опор с семантикой *cgtow.pts')
#
# dir_path = input('укажите путь к директории и нажмите Enter\nПуть:')
#
# # check if input correct
# if Path(dir_path).exists():
#     p = Path(dir_path)
#     cgtow = list(p.glob('*cgtow*'))[0]
#     dxf_files = list(p.glob('*.dxf'))  # list of dxf files
#
#     if not cgtow.exists():
#         input('ошибка - файл cgtow  не найден, нажмите Enter для выхода')
#         raise SystemExit()
#     elif len(dxf_files) > 3:
#         input('ошибка - количество dxf больше трех, нажмите Enter для выхода')
#         raise SystemExit()
#     elif len(dxf_files) == 0:
#         input('ошибка - dxf файлы не найдены, нажмите Enter для выхода')
#         raise SystemExit()
# else:
#     input('ошибка - рабочая директория задана не верно, нажмите Enter для выхода')
#     quit()


def dxf_poly_parse(path):
    """ создаем функцию парсер dxf """
    dxf = []  # list to write all data from file

    with open(path) as dxf_file:
        for line in dxf_file:
            dxf.append(line.strip())  # write each stroke to list

    polylines = []  # empty list for polylines
    line = []  # list for coords of each polyline

    for i in range(len(dxf)):
        if dxf[i] == 'POLYLINE':
            line = []  # list cleaning
        if dxf[i] == 'VERTEX' and dxf[i + 1] == '10':
            line.append((float(dxf[i + 2]), float(dxf[i + 4]), float(dxf[i + 6])))
        if dxf[i] == 'SEQEND':
            polylines.append(line)

    return polylines


def dist(x1, y1, x2, y2):
    """ расчет 2d расстояния """
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** (1 / 2)


def dist3d(x1, y1, z1, x2, y2, z2):
    """ расчет 3d расстояния """
    return round((((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)**(1/2)), 2)


# temp
p = Path(r'D:\python\some_tools\dxf_test\skb20')
cgtow = list(p.glob('*cgtow*'))[0]
dxf_files = list(p.glob('001*.dxf'))  # list of dxf files
#

# start here
tabs = []   # таблицы по каждой фазе
ctw = []   # будующий список координат опор
with cgtow.open() as f:
    spam = csv.reader(f, delimiter='\t', skipinitialspace=True)
    for row in spam:
        if not row[1] == '':
            ctw.append(row)


# проход по дхф файлам
mid_points = []   # list for mid points
for file in dxf_files:
    mids = []   # list of mid points for each phase
    phase = file.stem.split('_')[-1]   # name of phase
    polylines = dxf_poly_parse(file)   # calling function to have polylines

    # finding mid points    (можно сделать функцией)
    for line in range(len(polylines)):
        d1_min = d2_min = 1000000    # fake distance
        id_start = id_end = 'None'   # fake id
 
        st_x = polylines[line][0][0]
        st_y = polylines[line][0][1]
        end_x = polylines[line][-1][0]
        end_y = polylines[line][-1][1]
        
        # finding start and end ID
        for a in range(len(ctw)):
            # calc if one of other structures is closer to the start of polyline
            
            d2 = dist(st_x, st_y, float(ctw[a][1]), float(ctw[a][2]))
            
            if d2 < d1_min:
                d1_min = d2   # rewrite min dist
                id_start = ctw[a][0]   # rewrite id
                
        for b in range(len(ctw)):
            # calc if one of other structures is closer to the end of polyline
            d2 = dist(end_x, end_y, float(ctw[b][1]), float(ctw[b][2]))
            
            if d2 < d2_min:
                d2_min = d2   # rewrite min dist
                id_end = ctw[b][0]   # rewrite id
        
        mid_x = st_x - (st_x-end_x)/2
        mid_y = st_y - (st_y-end_y)/2
        
        # finding mid_z
        cv_num = len(polylines[line])//2   # central vertex number
        
        d_cv_mid = dist(polylines[line][cv_num][0], polylines[line][cv_num][1], mid_x, mid_y)
        d_b_vert = dist(polylines[line][cv_num][0], polylines[line][cv_num][1], polylines[line][cv_num+1][0], polylines[line][cv_num+1][1])
        mid_z = polylines[line][cv_num][2] - ((polylines[line][cv_num][2] - polylines[line][cv_num+1][2])*(d_cv_mid/d_b_vert))
        
        mids.append((phase, id_start, id_end, round(mid_x, 2),  round(mid_y, 2), round(mid_z, 2)))
    mid_points.append(mids)


mp = {}   # помещаем таблицы в словарь фаза: таблица
for tab in mid_points:
    mp[tab[0][0]] = pd.DataFrame(tab, columns=['phase', 'from', 'to', 'x', 'y', 'z'])

del(mid_points)

# добавляем в каждую таблицу колонку span
for key in mp.keys():
    mp[key]['span'] = mp[key][['from', 'to']].agg(' - '.join, axis=1)
    mp[key] = mp[key][['span', 'from', 'to', 'x', 'y', 'z']]



# 1 - расчет между фазами
# объединяем таблицы (сначала а и б, затем аб и с)
# mp_ab = mp['1a'].merge(mp['1b'][['span', 'x', 'y', 'z']], left_on='span', right_on='span', suffixes=('_1a', '_1b'))
# mp_abc = mp_ab.merge(mp['1c'][['span', 'x', 'y', 'z']], left_on='span', right_on='span', suffixes=(False, '_1c'))
#
# # переименовываем столбцы чтобы удобнее читалось
# mp_abc = mp_abc.rename(columns={'x': 'x_1c', 'y': 'y_1c', 'z': 'z_1c'})
#
# # упорядочиваем столбцы
# mp_abc = mp_abc[['span', 'from', 'to', 'x_1a', 'y_1a', 'z_1a', 'x_1b', 'y_1b', 'z_1b', 'x_1c', 'y_1c', 'z_1c']]
#
# # далее добавляем расчетные столбцы с расстояниями между фазами
# mp_abc['dist_ab'] = dist3d(mp_abc['x_1a'], mp_abc['y_1a'], mp_abc['z_1a'], mp_abc['x_1b'], mp_abc['y_1b'], mp_abc['z_1b'])
# mp_abc['dist_bc'] = dist3d(mp_abc['x_1b'], mp_abc['y_1b'], mp_abc['z_1b'], mp_abc['x_1c'], mp_abc['y_1c'], mp_abc['z_1c'])
# mp_abc['dist_ac'] = dist3d(mp_abc['x_1a'], mp_abc['y_1a'], mp_abc['z_1a'], mp_abc['x_1c'], mp_abc['y_1c'], mp_abc['z_1c'])
#
# # сохраняем координаты середин пролетов для каждой фазы:
# mp_abc.to_csv(path_or_buf='1a.txt', index=False, columns=['x_1a', 'y_1a', 'z_1a'], sep=' ', header=False)
# mp_abc.to_csv(path_or_buf='1b.txt', index=False, columns=['x_1b', 'y_1b', 'z_1b'], sep=' ', header=False)
# mp_abc.to_csv(path_or_buf='1c.txt', index=False, columns=['x_1c', 'y_1c', 'z_1c'], sep=' ', header=False)
#
# # сохраняем всю таблицу в xlsx
# mp_abc.to_excel("output_phases.xlsx")


# 2 - расчет тросов
# проверим есть ли тросы
ew_list = []
for key in mp.keys():
    if 'g' in key:
        ew_list.append(key)

# объединяем таблицы
if len(ew_list) > 0:
    for w in ew_list:
        spam_tab = mp[w]
        spam_phases = []
        for key in mp.keys():
            if key != w:
                spam_phases.append(key)   # add phase name to list
                spam_tab = spam_tab.merge(mp[key][['span', 'x', 'y', 'z']], left_on='span', right_on='span', suffixes=(str('_'+w), str('_'+key)))
                # переименовываем столбцы чтобы удобнее читалось (если это не последняя фаза)
                if len(spam_phases) != len(mp.keys())-1:
                    spam_tab = spam_tab.rename(columns={str('x_'+w): 'x', str('y_'+w): 'y', str('z_'+w): 'z'})

        # далее добавляем расчетные столбцы с расстояниями между фазами
        for wir in spam_phases:
            spam_tab[str('dist_to_'+wir)] = dist3d(spam_tab[str('x_'+w)], spam_tab[str('y_'+w)], spam_tab[str('z_'+w)],
                                                   spam_tab[str('x_'+wir)], spam_tab[str('y_'+wir)], spam_tab[str('z_'+wir)])

        # сохраняем всю таблицу в xlsx
        ew_path = p / f'{w}_output.xlsx'
        spam_tab.to_excel(ew_path, index=False)

#
# # сохраняем координаты середин пролетов для каждой фазы:
# mp_abc.to_csv(path_or_buf='1a.txt', index=False, columns=['x_1a', 'y_1a', 'z_1a'], sep=' ', header=False)
# mp_abc.to_csv(path_or_buf='1b.txt', index=False, columns=['x_1b', 'y_1b', 'z_1b'], sep=' ', header=False)
# mp_abc.to_csv(path_or_buf='1c.txt', index=False, columns=['x_1c', 'y_1c', 'z_1c'], sep=' ', header=False)








input("\nthe end\n\nнажмите Enter для выхода")
raise SystemExit()
