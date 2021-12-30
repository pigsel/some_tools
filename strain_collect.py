# сбор номеров анкерных опор из файлов спецификаций разных лет
#
# план
#
#     - выбрать папку и далее для каждой папки
#     - из названия взять год и номер линии
#     - из спецификации выбрать номера опор strain (после 2007 года из другой колонки)
#     - проверить из чего состоят номера - если есть название линии - убрать
#     - записать в общую таблицу - имя линии, номер анкерной опоры

from pathlib import Path
import pandas as pd

p = Path('D:\\work\\_TP\\for_22\\opten_archive')  # рабочая директория
fin_file_strain = p / 'all_strains.txt' # финальный текстовый файл с анкерами
fin_file_deleted = p / 'strains_to_delete.txt' # финальный текстовый файл с анкерами
all22 = p / 'all_22.txt' # все опоры проекта


global fin_strain_list, fin_delete_list
fin_strain_list = []
fin_delete_list = []


# читаем таблицу с именами и id номерами
tab_id = pd.read_csv(p / 'TP2022_list_of_objects.txt', sep='\t', header=0, index_col=0)

# Создаем список директорий
list_of_dirs = []
for x in p.iterdir():
     if x.is_dir(): list_of_dirs.append(x)


def rename_list(old_strain_list, line_name):
    # добавление имени линии к номеру опоры для 2002 и 2003 годов
    new_list = []
    good_list = []
    to_delete = []

    for i in old_strain_list:
        if len(str(i)) < 5:
            new_list.append(i)
        else:
            # print(i.upper(), 'ok')
            if i.upper().startswith(line_name):
                good_list.append(i)
            else:
                if line_name in i:
                    new_list.append(i.strip(line_name))
                else:
                    to_delete.append(i)
    for x in new_list:
        if type(x) == int:
            good_list.append(line_name + ('0' * (4 - len(str(x)))) + str(x))
        elif x.isdigit():
            good_list.append(line_name + ('0' * (4 - len(x)) + x))

        else:
            if x[:-1].isdigit() and not x[-1:].isdigit():
                good_list.append(line_name + ('0' * (5 - len(x)) + x))
            else:
                to_delete.append(x)

    return good_list, to_delete


def excel_2002(p_spec, line_name):
    # выборка номеров анкерных опор
    # в 2002 году несколько листов в эксель - выбираем нужный
    lists = pd.ExcelFile(p_spec).sheet_names  # see all sheet names
    strain_list =[]   # лист с анкерами - будет получен в конце
    to_delete = []
    list_name = 'none'

    if line_name in lists:
        list_name = line_name
    else:
        temp_name = line_name[:7] + ' ' + line_name[8:]  # меняем правый '-' на пробел
        list_name = temp_name

    # задаем имена столбцам, читаем только 1 и 8, header не указываем, имя листа нашли ранее
    spec_tab = pd.read_excel(p_spec, sheet_name=list_name, names=['pole', 'susp'], usecols=[0, 7], index_col=1)

    # из таблицы получаем список анкеров
    # ! - тут указано с заглавной буквы - возможен пропуск анкеров с маленькой
    if 'Strain' in spec_tab.index:
        strain_list = list(spec_tab.loc['Strain', 'pole'])

    strain_list, to_delete = rename_list(strain_list, line_name)

    return strain_list, to_delete


def excel_2003(p_spec, line_name):
    # выборка номеров анкерных опор
    # 2003 от 2002 отличается только одним листом в эксель
    strain_list =[]   # лист с анкерами - будет получен в конце
    # задаем имена столбцам, читаем только 1 и 8, header не указываем
    spec_tab = pd.read_excel(p_spec, names=['pole', 'susp'], usecols=[0, 7], index_col=1)

    # из таблицы получаем список анкеров
    # ! - тут указано с заглавной буквы - возможен пропуск анкеров с маленькой
    if 'Strain' in spec_tab.index:
        strain_list = list(spec_tab.loc['Strain', 'pole'])

    strain_list, to_delete = rename_list(strain_list, line_name)

    return strain_list, to_delete


def excel_2007(p_spec, line_name):
    # выборка номеров анкерных опор
    # начиная с 2007 года дут нормальные номера опор в колонке 2 (или 1 если начинать с 0)
    strain_list =[]   # лист с анкерами - будет получен в конце
    # задаем имена столбцам, читаем только 2 и 8, header не указываем
    spec_tab = pd.read_excel(p_spec, names=['pole', 'susp'], usecols=[1, 7], index_col=1)

    # из таблицы получаем список анкеров
    # ! - тут указано с заглавной буквы - возможен пропуск анкеров с маленькой
    if 'Strain' in spec_tab.index:
        strain_list = list(spec_tab.loc['Strain', 'pole'])

    strain_list, to_delete = rename_list(strain_list, line_name)

    return strain_list, to_delete


def excel_2015(p_spec):
    # выборка номеров анкерных опор
    # в 2015 году всё ок
    strain_list =[]   # лист с анкерами - будет получен в конце
    # задаем имена столбцам, читаем только 2 и 8, header не указываем
    spec_tab = pd.read_excel(p_spec, names=['pole', 'susp'], usecols=[1, 7], index_col=1)

    # из таблицы получаем список анкеров
    # ! - тут указано с заглавной буквы - возможен пропуск анкеров с маленькой
    if 'Strain' in spec_tab.index:
        strain_list = list(spec_tab.loc['Strain', 'pole'])
    return strain_list


def list_collect(line_path):
    # эта функция формирует список "хороших" номеров анкерных опор и опор для удаления
    # все это для отдельной папки - для одного объекта
    print('start list_collect')
    line_name = 'none'
    p_spec = 'none'
    strain_list = []
    to_delete =[]

    line_id = int(line_path.stem.split(sep='-')[0])  # номер линии 2022
    year = line_path.stem.split(sep='-')[1]  # год предыдущей обработки линии
    print(line_id, year)

    # поиск имени линии по индексу в таблице tab_id
    if line_id in tab_id.index:
        line_name = tab_id.loc[line_id, 'Line Name']
        print(line_name)
    else:
        print(f'! ошибка ! - {line_id} линия не найдена в списке')

    # поиск файла спецификации

    if len(list(line_path.glob('*pecification*.xls'))) == 1:
        p_spec = sorted(line_path.glob('*pecification*.xls'))[0]
        print(p_spec)
    else:
        print(' ! - ошибка поиска файла спецификации в линии - !')
        input(' - нажмите Enter для выхода - ')

    # в зависимости от года съемки выбираем как быть со спецификацией
    if int(year) == 2015:
        print('2006 + ')
        strain_list = excel_2015(p_spec)
    elif int(year) > 2003 and int(year) < 2015:
        print('- 2007-2010 -')
        strain_list, to_delete = excel_2007(p_spec, line_name)
    elif int(year) == 2003:
        print('- 2003 - ')
        strain_list, to_delete = excel_2003(p_spec, line_name)
    elif int(year) == 2002:
        print('- 2002 -')
        strain_list, to_delete = excel_2002(p_spec, line_name)
    else:
        print(' ! - ошибка - год съемки не распознан - !')
        input(' - нажмите Enter для выхода - ')


    for i in strain_list:
        fin_strain_list.append(i)
    for j in to_delete:
        fin_delete_list.append(j)

# собираем листы с номерами анкеров и отброшенных опор
for dir in list_of_dirs:
    list_collect(dir)

# сохраняем отброшенные в файл
with open(fin_file_deleted, 'w') as f:
    for struct in fin_delete_list:
        f.write(f'{struct}\n')

# открываем таблицу со всеми опорами проекта и мержим с таблицей из полученного листа
full_tab = pd.read_csv(all22, sep='\t', index_col=0, header=0)
str_tab = pd.DataFrame(fin_strain_list, index = fin_strain_list, columns = ['id'])
fin_tab = pd.merge(full_tab, str_tab, left_index=True, right_index=True)
fin_tab = fin_tab[['x', 'y', 'z']]   # удаляем лишний столбец

# сохраняем табличку
fin_tab.to_csv(fin_file_strain, sep='\t', mode='w', index_label='id', encoding='utf-8')


input('well done, press Enter to exit')
