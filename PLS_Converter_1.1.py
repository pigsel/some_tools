# -*- coding: utf-8 -*-
# for python 3
# created by Igor Bertyaev
# PLS Converter
# this program is for converting "x y z" or "c x y z" files to PLSCADD format with given feature code


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


def close_app():
    window.destroy()


def add_info(add_text):
    t_info.configure(state='normal')  # open to write
    t_info.insert(1.0, (f'\n{add_text}\n'))  # add text in the beginning (may be 'END' instead)
    t_info.configure(state='disabled')  # disable to write


def add_info2(add_text):
    t2_info.configure(state='normal')  # open to write
    t2_info.insert(1.0, (f'\n{add_text}\n'))  # add text in the beginning (may be 'END' instead)
    t2_info.configure(state='disabled')  # disable to write


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


def choose_pls():
    pls_path = fd.askopenfilename(title='файл экспорта из PLSCADD', filetypes=[('xyz files','.xyz'), ('all files','*.*')])  # pls select
    path_pls.delete(0, 'end')
    path_pls.insert(0, pls_path)  # past it to interface field
    add_info2(f'выбран файл: {pls_path}')


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
    add_info('... s t a r t ...')
    rename_files(p, proj_var.get())  # check folder and rename files if needed
    convert(p, proj_var.get())


def run_app2():
    p = Path(path_pls.get())  # get from interface field and convert from str to path
    v = r_var.get()+1
    add_info2(f'выбран файл: {p}\nвариант расчета: {v}')
    from_pls(p, v)
    add_info2('... Работа завершена ...')


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
    add_info('.... запуск обработки ....')
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
            n_tab[4] = str(f"{pts_path.stem.split('_')[1]}")
            n_tab[5] = '0.0'
            n_tab[[6, 7]] = "''"
            n_tab = n_tab[[3, 0, 1, 2, 4, 5, 6, 7]]

        elif len(n_tab.columns) == 4:
            n_tab[0] = n_tab.apply(lambda row: f"'{row[0]}'", axis=1)
            n_tab[4] = str(f"'{pts_path.stem.split('_')[2]}'")
            n_tab[5] = str(f"{pts_path.stem.split('_')[1]}")
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
                n_tab.to_csv(pls_path, sep=' ', mode='a', header=None, index=False)
            else:
                pls_path.write_text("TYPE='XYZ FILE' VERSION='4' UNITS='SI' SOURCE='OptenPingoConvertor'\n")
                n_tab.to_csv(pls_path, sep=' ', mode='a', header=None, index=False)
    add_info('.... Работа успешно завершена ....')


def from_pls(p, v):
    pls_tab = pd.read_csv(p, sep='\s+', quotechar="'", skiprows=1, header=None,
                          names=['suf', 'x', 'y', 'z', 'code', 'nol', 't_name', 'contract'])
    pls_tab = pls_tab.drop(['contract'], axis=1)  # drop this as it not use
    out_path = p.parent  # dir to save in

    if v == 1:
        pls_save(out_path, pls_tab[['x', 'y', 'z']], 'pls-out.txt')

    elif v == 2:
        pls_tab = pls_tab[['x', 'y', 'z', 'code']]
        code_list = list(pls_tab.code.unique())   # list of codes
        for code in code_list:
            spam = pls_tab.loc[lambda x: x['code'] == code, :]
            pls_save(out_path, spam[['x', 'y', 'z']], f'pls-{code}.txt')

    elif v == 3:
        pls_tab = pls_tab[['x', 'y', 'z', 'code', 't_name']].fillna('NA')   # заполняем NA где нет имени опоры
        code_list = list(pls_tab.code.unique())   # list of codes
        for code in code_list:
            spam = pls_tab.loc[lambda x: x['code'] == code, :]
            if len(spam.t_name.unique()) == 1 and spam.t_name.unique()[0] == 'NA':
                pls_save(out_path, spam[['x', 'y', 'z']], f'pls-{code}.txt')
            else:
                pls_save(out_path, spam[['t_name', 'x', 'y', 'z']], f'pls-{code}.txt')

    elif v == 4:
        pls_tab = pls_tab[['suf', 'x', 'y', 'z', 'code', 't_name']].fillna('NA')   # заполняем NA где нет имени опоры
        code_list = list(pls_tab.code.unique())  # list of codes
        for code in code_list:
            spam = pls_tab.loc[lambda x: x['code'] == code, :]
            suf_list = list(spam.suf.unique())  # list of suf
            for suf in suf_list:
                spam_spam = spam.loc[lambda x: x['suf'] == suf, :]
                if len(spam_spam.t_name.unique()) == 1 and spam_spam.t_name.unique()[0] == 'NA':
                    pls_save(out_path, spam_spam[['x', 'y', 'z']], f'pls-{code}-{suf}.txt')
                else:
                    pls_save(out_path, spam_spam[['t_name', 'x', 'y', 'z']], f'pls-{code}-{suf}.txt')


def pls_save(p, tab, name):
    if not (p / 'pls_out').exists(): (p / 'pls_out').mkdir()
    fin_path = p / 'pls_out' / name
    if fin_path.exists():  # check if exist
        new_dir = str(f'old_{int(time.time())}')  # replace old files to
        if not (p / 'pls_out' / new_dir).exists():
            (p / 'pls_out' / new_dir).mkdir()
        fin_path.replace(p / 'pls_out' / new_dir / name)

    tab.to_csv(fin_path, sep=' ', header=None, index=False, na_rep='NA', encoding='utf-8')



# ВНЕШНЯЯ ОБОЛОЧКА

def raise_frame(frame):
    frame.tkraise()


window = tk.Tk()
window.title("PLS converter")
#window.geometry("600x300") # size of the window when it opens
#window.minsize(width=600, height=600) # you can define the minimum size of the window like this
window.resizable(width="false", height="false") # change to false if you want to prevent resizing

f1 = tk.Frame(window)
f2 = tk.Frame(window)

for frame in (f1, f2):
    frame.grid(row=0, column=0, sticky='news')


# FRAME 1 - f1 = pts -> PLS  -------------------------------------

proj_dict = {'TP': tp, 'RTE': rte, 'Другой': no_proj}
proj_k = tuple(proj_dict.keys())
proj_var = tk.StringVar(f1)  # for project choose menu
proj_var.set(proj_k[0])   # default project 

# label on top that pts -> PLSCADD chosen (first page)
l_head1 = tk.Label(f1, text=" pts -> PLSCADD ", font="Veranda 14", width=35, height=2)
l_head1.grid(row=0, column=0, columnspan=2, sticky='we')

# button to choose second page 
button_to2 = tk.Button(f1, text=" PLSCADD -> pts", bd=0, bg='grey', font="Veranda 14",
                       activebackground='yellow', width=35, height=2, command=lambda:raise_frame(f2))
button_to2.grid(row=0, column=2, columnspan=2, sticky='we')

#  label 
l_dir = tk.Label(f1, text="Директория с файлами: ", font="Veranda 12")
l_dir.grid(row=1, column=0, sticky='e', pady=20, padx=10)

# field with path to work dir
path_to_dir = tk.Entry(f1, font="Veranda 12")
path_to_dir.grid(row=1, column=1, columnspan=3, sticky='we', pady=20, padx=10)

# button to choose work dir
button_search = tk.Button(f1, text=" ^ ", command=choose_dir)
button_search.grid(row=1, column=3, sticky='e', pady=20, padx=10)

#  label
l_xls = tk.Label(f1, text="Файл спецификации: ", font="Veranda 12")
l_xls.grid(row=2, column=0, sticky='e', pady=20, padx=10)

# field with path to xls
path_xls = tk.Entry(f1, font="Veranda 12")
path_xls.grid(row=2, column=1, columnspan=3, sticky='we', pady=20, padx=10)

# button to choose xls
button_xls = tk.Button(f1, text=" ^ ", command=choose_xls)
button_xls.grid(row=2, column=3, sticky='e', pady=20, padx=10)

# label
l_for = tk.Label(f1, text="Выбор проекта: ", font="Veranda 12")
l_for.grid(row=3, column=0, sticky='e', pady=10, padx=10)

# menu to choose project
proj_choose = tk.OptionMenu(f1, proj_var, *proj_k, command=proj_select)
proj_choose.config(width=15, font="Veranda 12")
proj_choose.grid(row=3, column=1, sticky='w', pady=10, padx=10)

# close button
button_close = tk.Button(f1, text="Выход", command=close_app, bg='red', bd = 0, font="Veranda 12")
button_close.grid(row=4, column=0, sticky='w'+'e', pady=20, padx=15)

# start button
button_run = tk.Button(f1, text="Запуск", command=run_app, bd=0, bg='light green', font="Veranda 12")
button_run.grid(row=4, column=3, sticky='w'+'e', pady=20, padx=15)

# text window
t_info = tk.Text(f1, font="Veranda 10", bg='white', relief='sunken', height=10, padx=20)
t_info.grid(row=5, column=0, columnspan=4, pady=20, padx=15, sticky='we')
scroll = tk.Scrollbar(f1, command=t_info.yview)
scroll.grid(row=5, pady=20, padx=15, column=3, sticky='enes')
t_info.config(yscrollcommand=scroll.set)


# текст
intro = str('1. Для перевода данных в формат PLSCADD укажите директорию с исходными данными\n'
           'после расчета в этой же директории будет создана папка "PLS" с выходными файлами.\n\n'
           '2. Если нужно, выберете файл Specification.xls c типами опор и контрактами (для TP)\n\n'
           '3. Выбор проекта позволяет не переименовывать файлы после FinAp,\n'
           'программа переименует их сама в соответствии с выбранным проектом.\n'
           'Если же файлы уже переименованы как надо, выбор проекта на расчет не повлияет')

# значения полей при запуске
add_info(intro)
path_to_dir.insert(0, 'укажите директорию с файлами')
path_xls.insert(0, 'нет')


# FRAME 2 - f2 = PLS -> pts ---------------------------

# label on top that pts -> PLSCADD chosen (first page)
l_head2 = tk.Label(f2, text=" PLSCADD -> pts ", font="Veranda 14", width=35, height=2)
l_head2.grid(row=0, column=2, columnspan=2, sticky='we')

# button to choose second page
button_to1 = tk.Button(f2, text=" pts -> PLSCADD ", bd=0, bg='grey', font="Veranda 14",
                       activebackground='yellow', width=35, height=2, command=lambda: raise_frame(f1))
button_to1.grid(row=0, column=0, columnspan=2, sticky='we')

#  label
l2_dir = tk.Label(f2, text="PLS файл: ", font="Veranda 12")
l2_dir.grid(row=1, column=0, sticky='e', pady=20, padx=10)

# field with path to work dir
path_pls = tk.Entry(f2, font="Veranda 12")
path_pls.grid(row=1, column=1, columnspan=3, sticky='we', pady=20, padx=10)

# button to choose work dir
button_pls = tk.Button(f2, text=" ^ ", command=choose_pls)
button_pls.grid(row=1, column=3, sticky='e', pady=20, padx=10)

#  label
l2_rad = tk.Label(f2, text="Вариант расчета: ", font="Veranda 12")
l2_rad.grid(row=2, column=0, sticky='e', pady=5, padx=10)

# radio button
r_var = tk.IntVar(f2)
r_var.set(1)

v1 = tk.Radiobutton(f2, text="1. Простой пересчет в один файл без разбиения",
                    variable=r_var, value=0, font="Veranda 10")
v1.grid(row=2, column=1, columnspan=3, sticky='w', pady=3, padx=10)
v2 = tk.Radiobutton(f2, text="2. Раздельные файлы по feature code, без семантики",
                    variable=r_var, value=1, font="Veranda 10")
v2.grid(row=3, column=1, columnspan=3, sticky='w', pady=3, padx=10)
v3 = tk.Radiobutton(f2, text="3. Раздельные файлы по feature code с семантикой (номера опор)",
                    variable=r_var, value=2, font="Veranda 10")
v3.grid(row=4, column=1, columnspan=3, sticky='w', pady=3, padx=10)
v4 = tk.Radiobutton(f2, text="4. Подробное разделение feature code и префикс (может получиться много файлов)",
                    variable=r_var, value=3, font="Veranda 10")
v4.grid(row=5, column=1, columnspan=3, sticky='w', pady=3, padx=10)


# close button
button_close = tk.Button(f2, text="Выход", command=close_app, bg='red', bd = 0, font="Veranda 12")
button_close.grid(row=6, column=0, sticky='we', pady=20, padx=15)

invis_l = tk.Label(f2, width=15, font="Veranda 12")
invis_l.grid(row=6, column=1, sticky='we', padx=10)

# start button
button_run = tk.Button(f2, text="Запуск", command=run_app2, bd = 0, bg = 'light green', font="Veranda 12")
button_run.grid(row=6, column=3, sticky='we', pady=20, padx=15)


# text window
t2_info = tk.Text(f2, font="Veranda 10", bg='white', relief='sunken', height=10, padx=20)
t2_info.grid(row=7, column=0, columnspan=4, pady=20, padx=15, sticky='we')
scroll2 = tk.Scrollbar(f2, command=t2_info.yview)
scroll2.grid(row=7, pady=20, padx=15, column=3, sticky='enes')
t2_info.config(yscrollcommand=scroll2.set)

intro2 = str('Для перевода файла из формата PLSCADD необходимо:\n'
             '1. Сам файл - экспорт его из PLSCADD или переведенный в этот формат ранее\n'
             '2. Выберете этот файл в меню выше\n'
             '3. Выберете подходящий вариант расчета\n'
             '4. В директории файла будет создана подпапка "pls-out", в которую запишется результат.\n'
             'Если директория уже существует и в ней имеются такие файлы они будут перемещены \n'
             'в подпапку " old_** " где ** - число - количество секунд на данный момент\n'
             )


add_info2(intro2)
path_pls.insert(0, 'выберете файл в PLSCADD формате')


raise_frame(f1)
window.mainloop()



# https://younglinux.info/tkinter/dialogbox.php

# import time
# start_time = time.time()
# main()
# print("--- %s seconds ---" % (time.time() - start_time))

