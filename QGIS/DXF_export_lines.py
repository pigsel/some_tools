# попытка сохранять слой с линиями в дхф
# каждый элемент будет сохраняться в слой с заданным именем

from pathlib import Path
import csv

p = Path(r'D:\work\_TP\for_22')

cline = []   #centerline 
c_name = ''  #имя каждой линии (берем из атрибутов)
body_text = ''   #текст кода дхф для записи в финальный файл


#функция для записи полилиний (ценртлайнов)
def polylines(cline, c_name):
    "создает часть файла с полилиниями (ценртлайн)"
    
    # переменные
    color = 2
    closed = 136   # для polyline 136 = не замкнуто, 9 = замкнуто 
    
    # header
    text = f'  0\nPOLYLINE\n 8\n{c_name}\n 62\n     {color}\n 70\n   {closed}\n'
    
    # for each vertex
    for n in range(len(cline)):
        text += f'  0\nVERTEX\n 10\n{cline[n][0]}\n 20\n{cline[n][1]}\n 30\n0\n'
    
    # closing polyline
    text += '  0\nSEQEND\n'
    
    #print(text)   # заменить на запись в файл
    return text


# далее часть работы со слоем qgis
layer = iface.activeLayer()
features = layer.getFeatures()
layer_name = f'{layer.name()}.dxf'
print(layer_name)
for f in features:
    o_name = f.attribute('o_fname')
    id = f.attribute('o_id')
    f_name = (f'{id}_{o_name}_topo')

    print(f_name)

    geom = f.geometry()
    part = 0
    for part in range(len(geom.asMultiPolyline())):
        li = []
        a = 0
        for a in range(len(geom.asMultiPolyline()[part])):
            li.append([geom.asMultiPolyline()[part][a].x(), geom.asMultiPolyline()[part][a].y()])
        body_text += polylines(li, f_name)


# а теперь соберем всё в один файл
p_dxf = p / layer_name
p_dxf.write_text('  0\nSECTION\n  2\nENTITIES\n' + body_text + '  0\nENDSEC\n  0\nEOF')
print('the end')


