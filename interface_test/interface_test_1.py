# more info https://younglinux.info/tkinter/tkinter
# -*- coding: utf-8 -*-
# for python 3
# created by Igor Bertyaev

from tkinter import *


def str_to_sort_list(event):
    s = ent.get()
    s = s.split()
    s.sort()
    lab['text'] = ' '.join(s)


root = Tk()

ent = Entry(width=20)
but = Button(text="Преобразовать")
lab = Label(width=20, bg='black', fg='white')

but.bind('<Button-1>', str_to_sort_list)

ent.pack()
but.pack()
lab.pack()
root.mainloop()
