# more info https://younglinux.info/tkinter/tkinter
# -*- coding: utf-8 -*-
# for python 3
# created by Igor Bertyaev
# sample of simple dialog box


import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from pathlib import Path


def add_info(add_text):
    t_info.configure(state='normal')  # open to write
    t_info.insert(1.0, (f'\n{add_text}\n'))  # add text in the beginning (may be 'END' instead)
    t_info.configure(state='disabled')  # disable to write


def run_app():
    p = Path(path_to_dir.get())  # get from interface field and convert from str to path
    add_info(f'выбрана директория: {p} ')
    add_info('... s t a r t ...')


def choose_dir():
    home_dir = fd.askdirectory(title='директория с *.pts файлами')  # directory select
    path_to_dir.delete(0, 'end')
    path_to_dir.insert(0, home_dir)  # past it to interface field
    add_info(f'выбрана директория {home_dir}')


def choose_xls():
    xls_path = fd.askopenfilename(title='Specification.xlsx', filetypes=[('xls files','.xls .xlsx')])  # xls select
    path_xls.delete(0, 'end')
    path_xls.insert(0, xls_path)  # past it to interface field
    add_info(f'файл спецификации: {xls_path}')


def close_app():
    window.destroy()


window = tk.Tk()
window.title("PLS converter")
#window.geometry("600x300") # size of the window when it opens
#window.minsize(width=600, height=600) # you can define the minimum size of the window like this


# label on top that pts -> PLSCADD chosen (first page)
l_head1 = tk.Label(text=" pts -> PLSCADD ", font="Veranda 14", width=35, height=2)
l_head1.grid(row=0, column=0, columnspan=2, sticky='we')


#  label
l_dir = tk.Label(text="Директория с файлами: ", font="Veranda 12")
l_dir.grid(row=1, column=0, sticky='e', pady=20, padx=10)

# field with path to work dir
path_to_dir = tk.Entry(font="Veranda 12")
path_to_dir.grid(row=1, column=1, columnspan=3, sticky='we', pady=20, padx=10)

# button to choose work dir
button_search = tk.Button(text=" ^ ", command=choose_dir)
button_search.grid(row=1, column=3, sticky='e', pady=20, padx=10)

#  label
l_xls = tk.Label(text="Файл спецификации: ", font="Veranda 12")
l_xls.grid(row=2, column=0, sticky='e', pady=20, padx=10)

# field with path to xls
path_xls = tk.Entry(font="Veranda 12")
path_xls.grid(row=2, column=1, columnspan=3, sticky='we', pady=20, padx=10)

# button to choose xls
button_xls = tk.Button(text=" ^ ", command=choose_xls)
button_xls.grid(row=2, column=3, sticky='e', pady=20, padx=10)

# close button
button_close = tk.Button(text="Выход", command=close_app, bg='red', bd = 0, font="Veranda 12")
button_close.grid(row=4, column=0, sticky='w'+'e', pady=20, padx=15)

# start button
button_run = tk.Button(text="Запуск", command=run_app, bd=0, bg='light green', font="Veranda 12")
button_run.grid(row=4, column=3, sticky='w'+'e', pady=20, padx=15)

# text window
t_info = tk.Text(font="Veranda 10", bg='white', relief='sunken', height=10, padx=20)
t_info.grid(row=5, column=0, columnspan=4, pady=20, padx=15, sticky='we')
scroll = tk.Scrollbar(command=t_info.yview)
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

window.mainloop()