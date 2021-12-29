# на входе список имен файлов с путями и новое имя для них.
# если путь с списке на замену, файл переименовывается в другую папку с новым именем.
# затем во всех файлах новой директории внутри файла заменяются старые пути новыми.

# коротко алгоритм:
# 1 ищем файл с путями
# 2 копируем себе его как лист
# 3 проходим по листу и
#     3.1. если путь к файлу содержит ХХХ то переименовываем файл
#     3.2. если нет то ничего не делаем
#
# 4. после прохода по всей таблице проходим по директории с новыми файлами
# и открыв каждый файл заменяем в нем пути новыми.


from pathlib import Path
import shutil

new_path = Path(r'D:\work\2021\TP_21\631_IGH-KIK-A\pls2\Structures\Tower\test')

p1 = Path(r'D:\work\2021\TP_21\631_IGH-KIK-A\pls2\Structures\Tower\C61\Type CJ\TOWER Models\Superseded\Rev A9')
p2 = Path(r'D:\work\2021\TP_21\631_IGH-KIK-A\pls2\Structures\Tower\C61\Type CL\TOWER Models')
p3 = Path(r'D:\work\2021\TP_21\631_IGH-KIK-A\pls2\Structures\Tower\C61\Type CK\TOWER Models\Superseded\Rev A\Rev A8')
pathstochange = [p1, p2, p3]

fileslistpath = Path(r'D:\work\2021\TP_21\631_IGH-KIK-A\pls2\Structures\Tower\test\list.txt')

filelist = []

with open(fileslistpath, 'r') as file:
    for line in file:
        words = line.split('\t')
        if len(words) == 2:
            filelist.append(words)

print(len(filelist))

for str in filelist:
    if Path(str[1]).parent in pathstochange:
        print('yes', str[0])
        shutil.copy(Path(str[1].strip('\n')), new_path / (str[0] + '.tow'))


# part 2

def find_to_replace(file_to_open):
    with open(file_to_open, 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace(r'\C61\Type CJ\TOWER Models\Superseded\Rev A9', '')
    filedata = filedata.replace(r'\C61\Type CL\TOWER Models', '')
    filedata = filedata.replace(r'\C61\Type CK\TOWER Models\Superseded\Rev A\Rev A8', '')

    # Write the file out again
    with open(file_to_open, 'w') as file:
        file.write(filedata)


for i in sorted(new_path.glob('*.tow')):
    find_to_replace(i)

input('done')
