# part 2 - continue of centrostruct
# in this part we use files from first run
# nd we calc azimuth of spans, line angle, structure angle and xarms


import numpy as np
import pandas as pd
from pathlib import Path
import csv
from math import sqrt, acos, sin, cos, radians, degrees


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


def cut_the_legs(array, cpoint):
    # couple of steps to cut the legs of structure

    np_str = np.array(array)   # to np array and then cut 1/3 from grd
    np_str_cut = np.delete(np_str, np_str[:, 2] < ((max(np_str[:, 2]) - min(np_str[:, 2])) / 3 + min(np_str[:, 2])), 0)

    # now add dist to cpoint and azimuth for each point in array
    spam = []
    for i in np_str_cut:
        spam.append(azimuth((cpoint[0], cpoint[1]), (i[0], i[1])))
    np_str_dist = np.append(np_str_cut, np.array(spam), axis=1)  # new array with azimuth and distance

    # delete points closer than 2m to center
    np_str_dist = np.delete(np_str_dist, np_str_dist[:, 4] < 2, 0)

    z_list = sorted(list(set(np_str_dist[:, 2])))   # just z coords, sorted w/o dubs
    gap_start = 0
    for i in range(len(z_list) - 1):
        if (z_list[i + 1] - z_list[i]) > 0.5:
            gap_start = z_list[i]   # level to cut legs (first gap 0.5m)
            break

    # cut again
    np_str_dist = np.delete(np_str_dist, np_str_dist[:, 2] < gap_start, 0)

    return np_str_dist


def xarms_levels(array, segment_size):
    segmented = []
    start = min(array)
    end = start + segment_size
    while end < max(array):
        segmented.append(sum(end > i > start for i in array))
        start += segment_size
        end += segment_size

    # then choose only bigger than mean
    ma = []
    biggest = 0
    biggest_nu = 0
    for nu, i in enumerate(segmented):
        if i > (np.mean(segmented)):
            ma.append(round((min(array) + segment_size * nu), 1))
        if i > biggest:
            biggest = i
            biggest_nu = nu

    big_one = round((min(array) + segment_size * biggest_nu), 1)

    return ma, big_one


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
    tow_cut = xyz_read(tempdir / str(f"{idx}_{cgt_tab.loc[idx, 'id']}_str.xyz"))    # read file
    cpoint = (cgt_tab.loc[idx, 'x1'], cgt_tab.loc[idx, 'y1'])  # center

    np_str_dist = cut_the_legs(tow_cut, cpoint)   # cut the legs (first part)

    # try to split xarms - first run
    first_run = sorted(xarms_levels(np_str_dist[:, 2], 1)[0])   # take 1m step

    # then split by arms
    arms = []
    for i in range(len(first_run)):
        # cut each arm bot and top
        spam = np.delete(np_str_dist, np_str_dist[:, 2] < first_run[i], 0)
        if i < len(first_run)-1:
            spam = np.delete(spam, spam[:, 2] > first_run[i+1], 0)
        arms.append(spam)

    # then work with each arm
    for i in range(len(arms)):
        # cut max density on 0.1m
        level = xarms_levels(arms[i][:, 2], 0.1)[1]  # max density
        arms[i] = np.delete(arms[i], arms[i][:, 2] < level - 0.1, 0)
        arms[i] = np.delete(arms[i], arms[i][:, 2] > level + 0.1, 0)

        # закончил здесь











ang_tab.to_excel(resultdir / "ang_tab.xlsx")  # save to xls

# creating DXF
p_dxf.write_text('  0\nSECTION\n  2\nENTITIES\n' + hor_axes(ang_tab) + '  0\nENDSEC\n  0\nEOF')

input('расчет завершен, нажмите Enter для выхода')
