### программа для сборки данных об опорах из таблиц в поддиректориях

from pathlib import Path
import pandas as pd

p = Path.cwd() / 'previous_opten'  # рабочая директория
tow_file_list = ['structure.xyz', 'tower.xyz', 'tower331.prn']  # возможные имена файлов
skip_folders = ['631_igh-kika_2002-53', '645_IGH-WPT-B_2002-54']
fin_file = Path.cwd() / 'previous_opten' / 'all_structures_opten.txt'

def tabs_build(f_path_1, f_path_2, opten_id, in_object, survey_year):
    # txt таблица с координатами (pls формат)
    tab_1 = pd.read_csv(f_path_1, sep='\s+', quotechar="'", skiprows=1, header=None, usecols=[6, 1, 2, 3], index_col=3)

    # заголовки для экселевской таблицы спецификации
    col_heads = ['Structure ID', 'Type tower', 'Contract', 'Высоты опор, м', 'Тип крепления (по лаз.данным)']
    # сама спецификация
    tab_2 = pd.read_excel(f_path_2, header=1, usecols=col_heads, index_col=0)

    # далее соединяем их в одну по индексу
    tab_3 = tab_1.join(tab_2)

    # теперь добавляем колонки
    # у нас уже есть id, x, y, z, Type tower, Contract, Высоты опор, Тип крепления
    # нужно добавить:
    #     1. line name - добавить из столбца ID
    #     2. in_object - из кода
    #     3. opten_id - из кода
    #     4. survey_year - из кода

    tab_3['line_name'] = tab_3.apply(lambda row: '-'.join(row.name.split('-')[1:]), axis=1)
    tab_3['in_object'] = tab_3.apply(lambda row: in_object, axis=1)
    tab_3['opten_id'] = tab_3.apply(lambda row: opten_id, axis=1)
    tab_3['survey_year'] = tab_3.apply(lambda row: survey_year, axis=1)


    # теперь сделаем экспорт в файл
    # сначала поставим колонки в правильном порядке
    tab_3 = tab_3[['line_name', 'in_object', 'opten_id', 'survey_year', 1, 2, 3, 'Contract', 'Type tower', 'Тип крепления (по лаз.данным)', 'Высоты опор, м']]
    tab_3.to_csv(fin_file, sep='\t', mode='a', header=None, na_rep='NA', encoding='utf-8')

for di in p.iterdir():  # looking for directories
    if di.is_dir() and di.name not in skip_folders:
        # print(di.name)  # list of dirs
        old_id = di.name.split(sep='-')[-1]
        in_object = di.name.split(sep='_')[1]
        opten_id = di.name.split(sep='_')[0]
        survey_year = di.name.split(sep='_')[-1].split(sep='-')[0]
        print(opten_id, in_object, survey_year)

        if 'a' in old_id:
            for letter in old_id:
                if letter.isalpha():
                    p_spam = di / letter
                    for file in p_spam.iterdir():
                        if file.name in tow_file_list:
                            f_path_1 = p_spam / file          # path to tab_1
                            print(f_path_1)
                    t_p = sorted(di.glob('*'+letter+'_'+in_object+'*pecification*.xls'))
                    if len(t_p) == 1:
                        f_path_2 = t_p[0]
                    else:
                        print(f' ! ошибка поиска файла спецификации в линии {opten_id}_{in_object}')
                        input(' - нажмите Enter для выхода - ')
                    print(f_path_2)
                    tabs_build(f_path_1, f_path_2, opten_id, in_object, survey_year)

        else:
            for file in di.iterdir():
                if file.name in tow_file_list:
                    f_path_1 = di / file  # path to tab_1
                    print(f_path_1)
                    t_p = sorted(di.glob('*pecification*.xls'))
                    if len(t_p) == 1:
                        f_path_2 = t_p[0]
                    else:
                        print(f' ! ошибка поиска файла спецификации в линии {opten_id}_{in_object}')
                        input(' - нажмите Enter для выхода - ')
                    print(f_path_2)
                    tabs_build(f_path_1, f_path_2, opten_id, in_object, survey_year)







'''
подсказки по pathlib

# directory tree 

def tree(directory):
    print(f'+ {directory}')
    for path in sorted(directory.rglob('*')):
        depth = len(path.relative_to(directory).parts)
        spacer = '    ' * depth
        print(f'{spacer}+ {path.name}')
        
tree(Path.cwd())


# list of files and dir

p = Path('.')
for x in p.iterdir(): print(x)

# или только папки 
for x in p.iterdir(): 
     if x.is_dir(): print(x)

# проверка
Path('folder_name').is_dir()
Out[22]: True

Path('folder_name').exists()
Out[23]: True

yes/no  - возвращает true / false
def check():
   ...:     answer = mb.askyesno(
   ...:         title="Вопрос", 
   ...:         message="Перенести данные?")
   ...:     if answer:
   ...:         print('yay !!!')


more
https://realpython.com/python-pathlib/
https://docs.python.org/3/library/pathlib.html

'''

'''
# подсказки по pandas

import pandas as pd
from pathlib import Path

# путь к файлу
src_file = Path.cwd() / 'previous_opten' / '631_igh-kika_2002-53' / 'tower331.prn'

n_tab = pd.read_csv(src_file, sep='\s+', index_col=0, header=0) # открываем таблицу
# sep='\s+' - разделитель пробел или несколько пробелов
# index_col=0 - первый столбец как индексы
# header=None - заголовков нет 
# quotechar="'" - убрать ковычки

# пример для Plscadd формата
# n_tab = pd.read_csv(src_file, sep='\s+', quotechar="'", skiprows=1, header=None, usecols=[6, 1, 2, 3], index_col=3)

# пример объединения столбцов 
left = pd.DataFrame({'key': ['foo', 'bar'], 'lval': [1, 2]})
right = pd.DataFrame({'key': ['foo', 'bar'], 'rval': [4, 5]})

left
   key  lval
0  foo     1
1  bar     2

right
   key  rval
0  foo     4
1  bar     5

pd.merge(left, right, on='key')
   key  lval  rval
0  foo     1     4
1  bar     2     5

# или по индексу
pd.merge(right, xox, left_index=True, right_index=True) 


# так будет соединять по индексу, если колонки тличаются, будет суффикс
left.join(right, lsuffix='_l', rsuffix='_r')
# так с указанием колонки 'key' как индекс
left.set_index('key').join(right.set_index('key'), lsuffix='_l', rsuffix='_r')



### excel

col_heads = ['Structure ID', 'Type tower', 'Contract', 'Высоты опор, м', 'Тип крепления (по лаз.данным)']
n_tab2 = pd.read_excel(src_file2, header=1, usecols=col_heads, index_col=0)


### save to file
tab3.to_csv('test_1.txt', sep='\t', mode='a', header=None, na_rep='NA', encoding='utf-8') 

some tips
#['A', 'B', 'C'] <-this is your columns order
df = df[['C', 'B', 'A']]  

tab3['line_name'] = tab3.apply (lambda row: '-'.join(row.name.split('-')[1:]), axis=1) # add column 'line_name'


'''