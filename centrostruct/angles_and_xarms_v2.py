# part 2 - continue of centrostruct
# in this part we use files from first run
# nd we calc azimuth of spans, line angle, structure angle and xarms


import numpy as np
import pandas as pd
from pathlib import Path
import csv
from math import sqrt, acos, sin, cos, radians, degrees


# пути
workdir = Path(r'D:\work\2022_m\220_man-van\test')
tempdir = workdir / 'temp'
#p_dxf = workdir / 'hor.dxf'


def azimuth(a, b):
    # by two points we get azimuth
    dx = round((a[0] - b[0]), 2)
    dy = round((a[1] - b[1]), 2)
    dist = round(sqrt(dx*dx + dy*dy), 2)    # dist a to b
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

    return np_str_dist


def xarms_levels(array, segment_size):
    segmented = []
    start = min(array)
    end = start + segment_size
    while end < max(array):
        segmented.append(sum(end > i > start for i in array))
        start += segment_size
        end += segment_size

    # then choose only bigger than mean *2
    ma = []
    biggest = 0
    biggest_nu = 0
    for nu, i in enumerate(segmented):
        if i > (np.mean(segmented) * 1.8):
            ma.append(round((min(array) + segment_size * nu), 1))
        if i > biggest:
            biggest = i
            biggest_nu = nu

    big_one = round((min(array) + segment_size * biggest_nu), 1)

    return sorted(ma), big_one


def xarms_levels_2(array, segment_size):
    segmented = []
    start = min(array)
    end = start + segment_size
    while end < max(array):
        segmented.append(sum(end > i > start for i in array))
        start += segment_size
        end += segment_size

    # then choose only bigger than max value*0.4
    ma = []
    biggest = 0
    biggest_nu = 0
    for nu, i in enumerate(segmented):
        if i > max(segmented) * 0.4:
            ma.append(round((min(array) + segment_size * nu), 1))
        if i > biggest:
            biggest = i
            biggest_nu = nu

    big_one = round((min(array) + segment_size * biggest_nu), 1)

    return sorted(ma), big_one


def group_arms(levels, segment_size):
    # group them if they close to each other

    new_levels = [levels[0]]  # add first one
    for i in range(1, len(levels)):
        if levels[i-1] + segment_size < levels[i]:
            new_levels.append(levels[i])

    return new_levels


def cutpart(part):
    part = np.array(part)
    part = np.delete(part, part[:, 3] > np.mean(part[:, 3]) + 25, 0)  # cut by angle
    part = np.delete(part, part[:, 3] < np.mean(part[:, 3]) - 25, 0)  # cut by angle
    part = np.delete(part, part[:, 4] < max(part[:, 4]) - 0.5, 0)  # cut from end

    return part


def aztocoords(az, length):
    dx = round(sin(radians(az)) * length, 2)
    dy = round(cos(radians(az)) * length, 2)

    return dx, dy


# creating DXF
def hor_axes(a_tab):
    # values
    color = 0
    text = ""   # future part of DXF with hor axes
    structures = []   # list of str to exclude dubs

    for n in range(len(a_tab)):
        idx = a_tab.iloc[n].name   # find index and work with it

        spam = a_tab.loc[idx, 'id']   # structure ID
        # check if it not in list
        if spam not in structures:
            structures.append(spam)

            for arm_name in ('x_arm 1', 'x_arm 2', 'x_arm 3'):
                # create 3 layers with xarms
                xarm = a_tab.loc[idx, arm_name]
                if not pd.isna(xarm):
                    # convert string to float
                    xarm = xarm.split(',')
                    for i in range(len(xarm)):
                        xarm[i] = float(xarm[i].strip('( )'))

                    layername = arm_name

                    # add header
                    text += f'0\nLINE\n 8\n{layername}\n 62\n     {color}\n'

                    # add first coords
                    text += f" 10\n{xarm[0]}\n 20\n{xarm[1]}\n 30\n{xarm[2]}\n"

                    # add second coords
                    text += f" 11\n{xarm[3]}\n 21\n{xarm[4]}\n 31\n{xarm[5]}\n"

    return text


# structure azimuth (middle of span az)
def az_str(az1, az2):
    az = (az1 + az2) / 2 - 90
    if az < 0:
        az += 360
    elif az > 360:
        az -= 360

    return az


# start here
# firstly get the initial table
cgt_tab = pd.read_csv(workdir / '220_v2.txt', delimiter='\t', index_col='index', encoding='cp1251')
# cgt_tab = pd.read_excel(resultdir / 'cgtw_output.xlsx', index_col=0)   # old vers
ang_tab = cgt_tab[['c_line', 'id']].copy()   # create new tab based of initial

# add new cols
new_cols = ['span name',
            'span length 2d',
            'span azimuth',
            'line angle',
            'structure azimuth',
            'x_arm start']

for col in new_cols:
    ang_tab[col] = np.nan

# find span name, length, azimuth, line angle
for n in range(len(cgt_tab) - 1):
    idx = cgt_tab.iloc[n].name  # find index and work with index

    if cgt_tab.loc[idx, 'c_line'] == cgt_tab.loc[idx + 1, 'c_line']:
        # check if we on the same c-line
        ang_tab.loc[idx, 'span name'] = f"{cgt_tab.loc[idx, 'id']} - {cgt_tab.loc[idx + 1, 'id']}"  # span id
        a = (cgt_tab.loc[idx, 'x_bot'], cgt_tab.loc[idx, 'y_bot'])  # start point
        b = (cgt_tab.loc[idx + 1, 'x_bot'], cgt_tab.loc[idx + 1, 'y_bot'])  # end point
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
    print('приступаем к опоре № ', n+1)
    idx = cgt_tab.iloc[n].name  # find index and work with index
    tow_cut = xyz_read(tempdir / str(f"{idx}_{cgt_tab.loc[idx, 'id']}_str.xyz"))    # read file
    cpoint = (cgt_tab.loc[idx, 'x_bot'], cgt_tab.loc[idx, 'y_bot'])  # center

    np_str_dist = cut_the_legs(tow_cut, cpoint)   # cut the legs to array

    # split xarms
    first_run = xarms_levels(np_str_dist[:, 2], 1)[0]  # take 1m step
    first_run = group_arms(first_run, 1)    # groups
    print('after first run ', first_run)

    # ориентируемся на три траверсы, но если нет то берем первую снизу
    if len(first_run) == 3:
        # cut again - try to get first arm and find the level more accurately, use -3 as it is 3th from top
        np_str_cut_1 = np.delete(np_str_dist, np_str_dist[:, 2] < first_run[-3] - 0.2, 0)  # bot side
        np_str_cut_1 = np.delete(np_str_cut_1, np_str_cut_1[:, 2] > first_run[-2], 0)  # top side
    else:
        np_str_cut_1 = np.delete(np_str_dist, np_str_dist[:, 2] < first_run[0] - 0.2, 0)  # bot side
        # np_str_cut_1 = np.delete(np_str_cut_1, np_str_cut_1[:, 2] > first_run[1], 0)  # top side

    # second run - more accurate - 0.1m segments - take only biggest value
    second_run = xarms_levels(np_str_cut_1[:,2], 0.1)[1]   # this is our start point now
    print('after second run ', second_run)
    ang_tab.loc[idx, 'x_arm start'] = second_run   # write to tab

    # this code does not work as expected, so do not use it
    # # final cut - low level - 0.2m
    # np_str_top = np.delete(np_str_dist, np_str_dist[:, 2] < second_run - 0.3, 0)
    #
    # # try to find each arm level
    # third_run = xarms_levels_2(np_str_top[:, 2], 0.1)[0]
    #
    # print('num of arms before group: ', third_run)
    # num_arms = group_arms(third_run, 0.3)    # bot levels of arms
    # print('num of arms: ', num_arms)
    # # if len(num_arms) > 3:
    # #     num_arms = num_arms[-3:]    # if there are more than 3 - leave top 3
    # #     print('!! corrected arms: ', num_arms)
    #
    # # divide by arms and cut 1.15m from the center (we use just lowest level of arms = 0.2m)
    # arms = []
    # for i in range(len(num_arms)):
    #     arms_len = []   # len, indx
    #     arm = np.delete(np_str_top, np_str_top[:, 2] < (num_arms[i] - 0.2), 0)  # cut bot
    #     arm = np.delete(arm, arm[:, 2] > (num_arms[i] + 0.2), 0)  # cut top
    #     arm = np.delete(arm, arm[:, 4] < 1.15, 0)  # cut by len 0 - 1.15
    #     if len(arm) != 0:
    #         arms.append(arm)
    #     for i in range(len(arms)):
    #         arms_len.append([len(arms[i]), i])
    #
    #     if len(num_arms) > 3:
    #         arms_len = sorted(arms_len)[:-3]
    #         for i in arms_len:
    #             #print(i)
    #             arms.pop(i[1])
    #
    # arm_axes = []

    # find structure azimuth
    if idx != 1:
        str_az = round(az_str(ang_tab.loc[idx, 'span azimuth'], ang_tab.loc[idx - 1, 'span azimuth']), 1)
    else:
        str_az = round(az_str(ang_tab.loc[idx, 'span azimuth'], ang_tab.loc[idx, 'span azimuth']), 1)
    print('structure azimuth: ', str_az)
    ang_tab.loc[idx, f'structure azimuth'] = str_az   # write to table


    # this part is not work well, so decided not to use it

    # for arm in arms:
    #     # for each arm
    #     # devide to 2 part by angle
    #     # find angle and max len for each part
    #
    #     first_part = []
    #     second_part = []
    #
    #     for ii in range(len(arm)):
    #         if ii != 0:
    #             if abs(arm[:,3][ii]-str_az) > 40:
    #                 second_part.append(list(arm[ii]))
    #             else:
    #                 first_part.append(list(arm[ii]))
    #         else:
    #             spam = arm[:,3][ii]
    #             first_part.append(list(arm[ii]))
    #
    #     print('разделено на две части: ', len(first_part), len(second_part))
    #
    #     # cut by length and angle
    #     if len(first_part) > 0 and len(second_part) > 0:
    #
    #         first_part = cutpart(first_part)
    #         second_part = cutpart(second_part)
    #
    #         first_az, sec_az = np.mean(first_part[:, 3]), np.mean(second_part[:,3])
    #         first_len, sec_len = max(first_part[:, 4]), max(second_part[:,4])
    #         first_h, sec_h = np.mean(sorted(first_part[:, 2])[:5]), np.mean(sorted(second_part[:,2])[:5])
    #
    #         first_shift = aztocoords(first_az, first_len)
    #         sec_shift = aztocoords(sec_az, sec_len)
    #
    #         start_pt = (round(cpoint[0], 2) + round(first_shift[0], 2),
    #                     round(cpoint[1], 2) + round(first_shift[1], 2),
    #                     round(first_h, 2))
    #         end_pt = (round(cpoint[0], 2) + round(sec_shift[0], 2),
    #                   round(cpoint[1], 2) + round(sec_shift[1], 2),
    #                   round(sec_h, 2))
    #
    #         arm_axes.append((start_pt, end_pt))
    #
    #     # finaly write them to the tab
    #     for i in range(len(arm_axes)):
    #         ang_tab.loc[idx, f'x_arm {i+1}'] = str(arm_axes[i])


ang_tab.to_excel(workdir / "ang_tab.xlsx")  # save to xls


# creating DXF
# p_dxf.write_text('  0\nSECTION\n  2\nENTITIES\n' + hor_axes(ang_tab) + '  0\nENDSEC\n  0\nEOF')

input('расчет завершен, нажмите Enter для выхода')
