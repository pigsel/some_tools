# -*- coding: utf-8 -*-
# for python 3
# created by Pingo
# pts_to_pls_v4
# this program is for converting "x y z" or "c x y z" files to plscadd format


import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from pathlib import Path
import pandas as pd
import time


# dict for projects / file mask and final name
tp = {
'attach520': 'attach_520_try.pts',
'attach522': 'attach_522_watt.pts',
'attach530': 'attach_530_catt.pts',
'attach521': 'attach_521_swp.pts',
'tower331': 'structure_331_base.pts',
'wire547': 'wire_547_cdr.pts',
'wire548': 'wire_548_wire.pts',
'331': 'structure_331_base.pts',
'332': 'structure-lrp_332_twr.pts',
'520': 'attach_520_try.pts',
'521': 'attach_521_swp.pts',
'522': 'attach_522_watt.pts',
'530': 'attach_530_catt.pts',
'547': 'wire_547_cdr.pts',
'548': 'wire_548_wire.pts',
'549': 'wire-lrp_549_lrp.pts',
'711': 'GIS-top_711_gisht.pts',
'712': 'GIS-xarm_712_gisx.pts',
'713': 'GIS-gnd-inf_713_gisitf.pts'
}

rte = {
'700': 'barycentre_700_bass.pts',
'710': 'barycentre_710_base.pts',
'720': 'sommet_720_top.pts',
'611': 'attach_611_catt.pts',
'621': 'attach_621_watt.pts',
'631': 'attach_631_swp.pts',
'811': 'wire_811_apcd.pts',
'812': 'wire_812_apcd.pts',
'813': 'wire_813_apcd.pts',
'821': 'wire_821_apcd.pts',
'822': 'wire_822_apcd.pts',
'823': 'wire_823_apcd.pts',
'831': 'wire_831_apcd.pts',
'832': 'wire_832_apcd.pts',
'833': 'wire_833_apcd.pts',
'841': 'wire_841_apcd.pts',
'842': 'wire_842_apcd.pts',
'843': 'wire_843_apcd.pts',
'800': 'wire_800_apwr.pts',
'801': 'wire_801_apwr.pts',
'803': 'wire_803_apwr.pts',
'610': 'wire_610_cdr.pts',
'620': 'wire_620_wire.pts',
'750': 'structure_750_str.pts'
}

no_proj = {}  # в случае если нет проекта


proj_dict = {'TP': tp, 'RTE': rte, 'Другой': no_proj}
proj_k = tuple(proj_dict.keys())


def close_app():
    window.destroy()


def add_info(add_text):
    t_info.configure(state='normal')  # open to write
    t_info.insert(1.0, (f'\n{add_text}\n'))  # add text in the beginning (may be 'END' instead)
    t_info.configure(state='disabled')  # disable to write


def proj_select(selection):
    add_info(f'выбран проект {proj_var.get()}')


def choose_dir():
    home_dir = fd.askdirectory(title='директория с *.pts файлами')  # directory select
    path_to_dir.delete(0, 'end')
    path_to_dir.insert(0, home_dir)  # past it to interface field
    add_info(f'выбрана директория {home_dir}')


def choose_xls():
    xls_path = fd.askopenfilename(title='Specification.xls', filetypes=[('xls files','.xls .xlsx')])  # xls select
    path_xls.delete(0, 'end')
    path_xls.insert(0, xls_path)  # past it to interface field
    add_info(f'файл спецификации: {xls_path}')

def add_typetower(xl_path, tab):
    add_info(f'импортируем типы опор и контракты из {xl_path.name}')
    # заголовки для экселевской таблицы спецификации
    col_heads = ['Structure ID', 'Type tower', 'Contract']
    # сама спецификация
    spec_tab = pd.read_excel(xl_path, header=1, usecols=col_heads, index_col=0)
    spec_tab = spec_tab[['Type tower', 'Contract']].fillna('NA')  # заменяем пустые значения на NA


    tab[8] = tab.apply(lambda row: row[0].strip("'"), axis=1)  # в плс таблице добавляем колонку с именами без'
    tab = tab.set_index(8).join(spec_tab)  # присоединяем к tab колонки из спецификации, перед этим колока 8 устанавливается как индекс
    tab[7] = tab.apply(lambda row: f"'{row['Contract']}_{row['Type tower']}'", axis=1)   # в колонку 6 вставляем контракт и тип
    tab = tab.drop(['Type tower', 'Contract'], axis=1)   # теперь не нужные колонки удаляем
    return tab


def run_app():
    p = Path(path_to_dir.get())  # get from interface field and convert from str to path
    add_info(f'выбрана директория: {p} \nвыбран проект: {proj_var.get()}')
    rename_files(p, proj_var.get())  # check folder and rename files if needed
    convert(p, proj_var.get())


def rename_files(p, proj_work):
    pro = proj_dict[proj_work]  # use project dict to select dict for rename
    if not pro == no_proj:   # if no_proj no needs for rename
        fz0 = []  # list of input files
        if p.exists():    # check if folder exist
            for suf in ('*.pts', '*.xyz', '*.txt'):
                for i in sorted(p.glob(suf)):   # append all *.pts *.xyz or *.txt files names to fz0
                    fz0.append(i.name)
            for i in fz0:
                if i.split('.')[0] in pro.keys():    # keys in dict are without suffix
                    old = p / i
                    new = p / pro[i.split('.')[0]]
                    old.rename(new)
            add_info('файлы переименованы')
        else:
            add_info('! ошибка выбора директории !')


def convert(p, proj_work):
    pro = proj_dict[proj_work]  # use project dict to select dict for rename
    fz0 = []  # list of input files
    for i in sorted(p.glob('*.pts')):  # append all *.pts files names to fz0
        if i.stat().st_size > 0:
            if pro == no_proj or i.name in pro.values():  # if no_proj no need to chek
                fz0.append(i.name)
            else:
                answer = mb.askyesno(title='! ОШИБКА !', message=str(f' ! возможно ошибка в имени файла: {i.name} ! '
                                                                     f'\n не похоже на Feature Code проекта {proj_work}'
                                                                     f'\n ?? конвертировать данный файл в PLS ??'))
                if answer: fz0.append(i.name)  # отработка ошибки если имя файла не совпадает с feature code
    add_info(f"выбраны файлы для обработки: {', '.join(fz0)}")

    p_out = p / 'PLS'
    if p_out.exists():  # check if dir PLS exist
        new_name = str(f'{p_out}_{int(time.time())}')  # rename old PLS dir - add seconds to its name
        p_out.rename(new_name)
    p_out.mkdir() # creating new PLS dir

    for file in fz0:
        err = 0
        pts_path = p / file
        n_tab = pd.read_csv(pts_path, sep='\s+', header=None)
        if len(n_tab.columns) == 3:
            n_tab[3] = str(f"'{pts_path.stem.split('_')[2]}'")
            n_tab[4] = str(f"'{pts_path.stem.split('_')[1]}'")
            n_tab[5] = '0.0'
            n_tab[[6, 7]] = "''"
            n_tab = n_tab[[3, 0, 1, 2, 4, 5, 6, 7]]
        elif len(n_tab.columns) == 4:
            n_tab[0] = n_tab.apply(lambda row: f"'{row[0]}'", axis=1)
            n_tab[4] = str(f"'{pts_path.stem.split('_')[2]}'")
            n_tab[5] = str(f"'{pts_path.stem.split('_')[1]}'")
            n_tab[6] = '0.0'
            n_tab[7] = "''"
            n_tab = n_tab[[4, 1, 2, 3, 5, 6, 0, 7]]
            if path_xls.get() != 'нет':
                n_tab = add_typetower(Path(path_xls.get()), n_tab)

        else:
            add_info('ошибка файла')
            err = 1

        if not err == 1:
            pls_name = str(f'{file.split("_")[0]}.xyz')  # file to write in
            pls_path = p_out / pls_name
            if pls_path.exists():  # check if exist
                n_tab.to_csv(pls_path, sep=' ', mode='a', header=None, index=False, na_rep='NA', encoding='utf-8')
            else:
                pls_path.write_text("TYPE='XYZ FILE' VERSION='4' UNITS='SI' SOURCE='OptenPingoConvertor'\n")
                n_tab.to_csv(pls_path, sep=' ', mode='a', header=None, index=False, na_rep='NA', encoding='utf-8')
    add_info('работа завершена')



# ВНЕШНЯЯ ОБОЛОЧКА
window = tk.Tk()
window.title("PLS converter") 
#window.geometry("600x300") # size of the window when it opens
#window.minsize(width=600, height=600) # you can define the minimum size of the window like this
window.resizable(width="false", height="false") # change to false if you want to prevent resizing


proj_var = tk.StringVar()  # for project choose menu
proj_var.set(proj_k[0])   # default project 

# label on top that pts -> PLSCADD chosen (first page)
l_head1 = tk.Label(text=" pts -> PLSCADD ", font=("Veranda 14"), width=35, heigh=2)
l_head1.grid(row=0, column=0, columnspan=2, sticky='w'+'e')

# button to choose second page 
button_to2 = tk.Button(text=" PLSCADD -> pts", bd = 0, bg = 'grey', font=("Veranda 14"), activebackground = 'yellow', width=35, heigh=2)
button_to2.grid(row=0, column=2, columnspan=2, sticky='w'+'e')

#  label 
l_dir = tk.Label(text="Директория с файлами: ", font=("Veranda 12"))
l_dir.grid(row=1, column=0, sticky='e', pady=20, padx=10)

# field with path to work dir
path_to_dir = tk.Entry(font=("Veranda 12"))
path_to_dir.grid(row=1, column=1, columnspan=3, sticky='w'+'e', pady=20, padx=10)

# button to choose work dir
button_search = tk.Button(text=" ^ ", command=choose_dir)
button_search.grid(row=1, column=3, sticky='e', pady=20, padx=10)

#  label
l_xls = tk.Label(text="Файл спецификации: ", font=("Veranda 12"))
l_xls.grid(row=2, column=0, sticky='e', pady=20, padx=10)

# field with path to xls
path_xls = tk.Entry(font=("Veranda 12"))
path_xls.grid(row=2, column=1, columnspan=3, sticky='w'+'e', pady=20, padx=10)

# button to choose xls
button_xls = tk.Button(text=" ^ ", command=choose_xls)
button_xls.grid(row=2, column=3, sticky='e', pady=20, padx=10)

# label
l_for = tk.Label(text="Выбор проекта: ", font=("Veranda 12"))
l_for.grid(row=3, column=0, sticky='e', pady=10, padx=10)

# menu to choose project
proj_choose = tk.OptionMenu(window, proj_var, *proj_k, command=proj_select)
proj_choose.config(width = 15, font=("Veranda 12"))
proj_choose.grid(row=3, column=1, sticky='w', pady=10, padx=10)

# close button
button_close = tk.Button(text="Выход", command=close_app, bg='red', bd = 0, font=("Veranda 12"))
button_close.grid(row=4, column=0, sticky='w'+'e', pady=20, padx=15)

# start button
button_run = tk.Button(text="Запуск", command=run_app, bd = 0, bg = 'light green', font=("Veranda 12"))
button_run.grid(row=4, column=3, sticky='w'+'e', pady=20, padx=15)

# text window
# l_info = tk.Label(text=info, font=("Veranda 10"), justify='left', bg='white', relief='sunken', heigh=10)
# l_info.grid(row=4, column=0, columnspan=4, pady=20, padx=15, sticky='w'+'e')
t_info = tk.Text(font=("Veranda 10"), bg='white', relief='sunken', heigh=10, padx=20)
t_info.grid(row=5, column=0, columnspan=4, pady=20, padx=15, sticky='w'+'e')
scroll = tk.Scrollbar(command=t_info.yview)
scroll.grid(row=5, pady=20, padx=15, column=3, sticky='en'+'es')
t_info.config(yscrollcommand=scroll.set)


# текст
inro = str('1. Для перевода данных в формат PLSCADD укажите директорию с исходными данными\n'
           'после расчета в этой же директории будет создана папка "PLS" с выходными файлами.\n\n'
           '2. Если нужно, выберете файл Specification.xls c типами опор и контрактами (для TP)\n\n'
           '3. Выбор проекта позволяет не переименовывать файлы после FinAp,\n'
           'программа переименует их сама в соответствии с выбранным проектом.\n'
           'Если же файлы уже переименованы как надо, выбор проекта на расчет не повлияет')

# значения полей при запуске
add_info(inro)
path_to_dir.insert(0, 'укажите директорию с файлами')
path_xls.insert(0, 'нет')

window.mainloop()







# https://younglinux.info/tkinter/dialogbox.php

# #example  2  два окна
# from tkinter import *
#
#
# def raise_frame(frame):
#     frame.tkraise()
#
# root = Tk()
#
# f1 = Frame(root)
# f2 = Frame(root)
# f3 = Frame(root)
# f4 = Frame(root)
#
# for frame in (f1, f2, f3, f4):
#     frame.grid(row=0, column=0, sticky='news')
#
# Button(f1, text='Go to frame 2', command=lambda:raise_frame(f2)).pack()
# Label(f1, text='FRAME 1').pack()
#
# Label(f2, text='FRAME 2').pack()
# Button(f2, text='Go to frame 3', command=lambda:raise_frame(f3)).pack()
#
# Label(f3, text='FRAME 3').pack(side='left')
# Button(f3, text='Go to frame 4', command=lambda:raise_frame(f4)).pack(side='left')
#
# Label(f4, text='FRAME 4').pack()
# Button(f4, text='Goto to frame 1', command=lambda:raise_frame(f1)).pack()
#
# raise_frame(f1)
# root.mainloop()

# import time
# start_time = time.time()
# main()
# print("--- %s seconds ---" % (time.time() - start_time))