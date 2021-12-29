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
fin_file = p / 'all_strains.txt' # финальный текстовый файл с анкерами

# читаем таблицу с именами и id номерами
tab_id = pd.read_csv(p / 'TP2022_list_of_objects.txt', sep='\t', header=0, index_col=0)

# Создаем список директорий
list_of_dirs = []
for x in p.iterdir():
     if x.is_dir(): list_of_dirs.append(x)


def excel_2002(p_spec, line_name):
    # выборка номеров анкерных опор
    # в 2002 году несколько листов в эксель - выбираем нужный
    lists = pd.ExcelFile(p_spec).sheet_names  # see all sheet names
    strain_list =[]   # лист с анкерами - будет получен в конце

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
    return strain_list


def list_collect(line_path):
    # эта функция формирует список "хороших" номеров анкерных опор и опор для удаления
    # все это для отдельной папки - для одного объекта
    print('start list_collect')
    line_name = 'none'
    p_spec = 'none'
    list_name = 'none'

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
    if int(year) > 2006:
        print('2006 + ')
    elif int(year) == 2003:
        print('- 2003 -')
    elif int(year) == 2002:
        print('- 2002 -')
        strain_list = excel_2002(p_spec, line_name)
        print(strain_list)
    else:
        print(' ! - ошибка - год съемки не распознан - !')
        input(' - нажмите Enter для выхода - ')


list_collect(p / '2202-2002-12')

input('done')