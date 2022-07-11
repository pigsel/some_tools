# part 2 - continue of centrostruct
# in this part we use files from first run
# nd we calc azimuth of spans, line angle, structure angle and xarms


import numpy as np
import pandas as pd
from pathlib import Path
from shapely.geometry import Point, MultiPoint, LineString, MultiLineString
import csv
from math import sqrt, acos, degrees


# пути
workdir = Path(r'D:\work\2022_m\training\ok')
resultdir = workdir / 'result'
tempdir = workdir / 'temp'
p_dxf = resultdir / 'hor.dxf'


def azimuth(a, b):
    # by two points we get azimuth
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dist = round(sqrt(dx*dx + dy*dy), 3)    # dist a to b
    dx2 = abs(dx)
    beta = degrees(acos(dx2/dist))
    if dx > 0:
        if dy < 0:
            angle = 270 + beta
        else:
            angle = 270 - beta
    else:
        if dy < 0:
            angle = 90 - beta
        else:
            angle = 90 + beta

    return round(angle, 1), dist


def xyz_read(path):
    # read xyz arrays from files
    with open(path, newline='') as xyz_file:
        spamlist = []
        spamreader = csv.reader(xyz_file, delimiter=' ', quoting=csv.QUOTE_NONNUMERIC, skipinitialspace=True)
        for row in spamreader:
            spamlist.append(row)

    return spamlist


def xarms_levels(array, segment_size):
    segmented = []
    start = min(array)
    end = start + segment_size
    while end < max(array):
        segmented.append(sum(end > i > start for i in array))
        start += segment_size
        end += segment_size

    # then choose only biggest than mean*2
    ma = []
    for nu, i in enumerate(segmented):
        if i > (np.mean(segmented) * 2):
            ma.append((nu, i))

    # then group them if they close to each other
    ma2 = {}
    low_level = 0
    points_sum = 0

    for i in range(len(ma)):
        # если следующий сегмент также отобран
        if i != len(ma) - 1 and ma[i][0] + 1 == (ma[i + 1][0]):
            points_sum += ma[i + 1][1]

            # если предыдущий сегмент не был отобран
            if i > 0 and not ma[i][0] - 1 == (ma[i - 1][0]):
                points_sum += ma[i][1]
                low_level = ma[i][0]

            ma2[low_level] = points_sum

        else:
            # print('skip')
            low_level = 0
            points_sum = 0

    #  из отобранных групп выделяем три наибольшие
    # такой отбор не стаботает на траверсах постоянной высоты - там будет по два выброса на траверсу
    selected = sorted(ma2.items(), key=lambda item: item[1])[-3:]
    # print(selected)

    h_trav = []  # нижие кромки траверс
    for i in selected:
        h_trav.append(round((min(array) + segment_size * i[0]), 1))
    # print(sorted(h_trav))

    return sorted(h_trav)[0]


def midpoint(p1, p2):
    # calc middle point
    mx = round((p1[0] + p2[0]) / 2, 2)
    my = round((p1[1] + p2[1]) / 2, 2)

    return (mx, my)


# creating DXF
def hor_axes(a_tab):
    # values
    layername = 'Hor'
    color = 0
    text = ""   # future part of DXF with hor axes
    structures = []   # list of str to exclude dubs

    for n in range(len(a_tab)):
        idx = a_tab.iloc[n].name   # find index and work with it

        spam = a_tab.loc[idx, 'id']   # structure ID
        # check if it not in list
        if spam not in structures:
            structures.append(spam)
            xarm = a_tab.loc[idx, 'x_arm geometry'].coords


            # add header
            text += f'0\nLINE\n 8\n{layername}\n 62\n     {color}\n'

            # add first coords
            text += f" 10\n{xarm[0][0]}\n 20\n{xarm[0][1]}\n 30\n{a_tab.loc[idx, 'x_arm start']}\n"

            # add second coords
            text += f" 11\n{xarm[1][0]}\n 21\n{xarm[1][1]}\n 31\n{a_tab.loc[idx, 'x_arm start']}\n"

    return text


# start here
# firstly get the initial table
cgt_tab = pd.read_excel(resultdir / 'cgtw_output.xlsx', index_col=0)
ang_tab = cgt_tab[['c_line', 'id']].copy()   # create new tab based of initial

# add new cols
new_cols = ['span name', 'span length 2d', 'span azimuth', 'line angle', 'structure azimuth', 'structure rotation', 'x_arm start', 'x_arm geometry']
for col in new_cols:
    ang_tab[col] = np.nan

# find span name, length, azimuth, line angle
for n in range(len(cgt_tab) - 1):
    idx = cgt_tab.iloc[n].name  # find index and work with index

    if cgt_tab.loc[idx, 'c_line'] == cgt_tab.loc[idx + 1, 'c_line']:
        # check if we on the same c-line
        ang_tab.loc[idx, 'span name'] = f"{cgt_tab.loc[idx, 'id']} - {cgt_tab.loc[idx + 1, 'id']}"  # span id
        a = (cgt_tab.loc[idx, 'x1'], cgt_tab.loc[idx, 'y1'])  # start point
        b = (cgt_tab.loc[idx + 1, 'x1'], cgt_tab.loc[idx + 1, 'y1'])  # end point
        ang_tab.loc[idx, 'span azimuth'], ang_tab.loc[idx, 'span length 2d'] = azimuth(a, b)
        if idx > 1:
            if cgt_tab.loc[idx, 'c_line'] == cgt_tab.loc[idx - 1, 'c_line']:
                spam = ang_tab.loc[idx, 'span azimuth'] - ang_tab.loc[idx - 1, 'span azimuth']
                if spam < -180:
                    ang_tab.loc[idx, 'line angle'] = spam + 360
                else:
                    ang_tab.loc[idx, 'line angle'] = spam
            else:
                ang_tab.loc[idx, 'line angle'] = 0
        else:
            ang_tab.loc[idx, 'line angle'] = 0

    # print(span_name, azim, span_len)


# let's work with x-arms
for n in range(len(cgt_tab)):
    idx = cgt_tab.iloc[n].name  # find index and work with index
    tow_cut = xyz_read(tempdir / str(f"{idx}_{cgt_tab.loc[idx, 'id']}_str.xyz"))

    np_str = np.array(tow_cut)
    np_str_z = np_str[:, 2]  # leave only z-coord
    np_str_z = np.delete(np_str_z, np_str_z < max(np_str_z) - 20, 0)  # cut 20 m from top

    z1 = xarms_levels(np_str_z, 0.1)  # find xarm levels
    ang_tab.loc[idx, 'x_arm start'] = z1   # write to tab

    # cut the legs again (more accurate)
    np_str_cut = np.delete(np_str, np_str[:,2]<(z1-0.1), 0)

    # now work with top part
    np_str_mp = MultiPoint(np_str_cut)    # to multipoint (needs to shapely)
    rect = np_str_mp.minimum_rotated_rectangle
    rect_c = rect.centroid

    # find a longest side and azimuth
    side_a = azimuth(list(rect.exterior.coords)[0], list(rect.exterior.coords)[1])
    side_b = azimuth(list(rect.exterior.coords)[1], list(rect.exterior.coords)[2])
    if side_a[1] > side_b[1]:
        str_azmt = side_a[0]
        axl = LineString([midpoint(list(rect.exterior.coords)[0], list(rect.exterior.coords)[3]),
                          midpoint(list(rect.exterior.coords)[1], list(rect.exterior.coords)[2])])
    else:
        str_azmt = side_b[0]
        axl = LineString([midpoint(list(rect.exterior.coords)[0], list(rect.exterior.coords)[1]),
                          midpoint(list(rect.exterior.coords)[2], list(rect.exterior.coords)[3])])

    print(axl.length)
    print(axl)
    print(str_azmt)
    ang_tab.loc[idx, 'structure rotation'] = str_azmt
    ang_tab.loc[idx, 'x_arm geometry'] = axl


ang_tab.to_excel(resultdir / "ang_tab.xlsx")  # save to xls

# creating DXF
p_dxf.write_text('  0\nSECTION\n  2\nENTITIES\n' + hor_axes(ang_tab) + '  0\nENDSEC\n  0\nEOF')

input('расчет завершен, нажмите Enter для выхода')
