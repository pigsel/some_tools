# сохранение коридора в дхф
# коридор сохранится как набор полилиний

from pathlib import Path
import csv


p = Path(r'D:\work\_TP\for_22\dxf')


# далее часть работы со слоем qgis
layer = iface.activeLayer()
features = layer.getFeatures()

for f in features:

    geom = f.geometry()
xx=1
a=[]
for n in geom.asMultiPolygon():
    print(f'part len: {len(n)}')
    for nn in n:
        print(len(nn))
        p_dxf = p / f'{xx}.txt'
        with open(p_dxf, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerows(nn)
        xx+=1

print('the end of part 1')

# part 2 - read txt and write to dxf

# count files
list_of_files = list(p.glob('*.txt'))

# сделаем функцию для записи полилиний (ценртлайнов)
def polylines(cline):
    "создает часть файла с полилиниями (ценртлайн)"
    
    # переменные
    layername = 'Coridor'
    color = 5
    closed = 136   # для polyline 136 = не замкнуто, 9 = замкнуто 
    
    # header
    text = f'  0\nPOLYLINE\n 8\n{layername}\n 62\n     {color}\n 70\n   {closed}\n'
    
    # for each vertex
    for n in range(len(cline)):
        text += f'  0\nVERTEX\n 10\n{cline[n][0]}\n 20\n{cline[n][1]}\n 30\n0\n'
    
    # closing polyline
    text += '  0\nSEQEND\n'
    
    #print(text)   # заменить на запись в файл
    return text

allthetext=''

for file in list_of_files:
    cline = []
    with file.open() as f:
        spamreader = csv.reader(f, delimiter=' ', skipinitialspace=True)
        for row in spamreader:
            cline.append(row)
    allthetext += polylines(cline)
    
# а теперь соберем всё в один файл
p_dxf = p / 'result.dxf'
p_dxf.write_text('  0\nSECTION\n  2\nENTITIES\n' + allthetext + '  0\nENDSEC\n  0\nEOF')

print('the end of part 2')