# creating spans
import csv
from pathlib import Path

# path to file *start_id end_id*
p = Path(r'D:\work\2021\max_den_proj\gis\spans.txt')

# read file and save it to list
ws = [] # spans
with p.open() as f:
    spamreader = csv.reader(f, delimiter='\t', skipinitialspace=True)
    for row in spamreader:
        ws.append(row)

# create layer for lines
wsl = iface.addVectorLayer("LineString?crs=EPSG:32647", "spans", "memory")
# add atributes to the layer
from qgis.PyQt.QtCore import QVariant
pr = wsl.dataProvider()
pr.addAttributes([QgsField("from", QVariant.String),
                  QgsField("to", QVariant.String)])
wsl.updateFields() 

for i in ws:
    point_1 = point_2 = 0
    print(i)
    # searching coordinates in layer
    # layer = iface.activeLayer()
    layer = QgsVectorLayer("D:/work/2021/max_den_proj/gis/qgis_example.gpkg|layername=structures")
    for fe in layer.getFeatures():
        if fe.attribute('Имя опоры') == i[0]:
            point_1 = QgsPoint(fe.geometry().asPoint())
        elif fe.attribute('Имя опоры') == i[1]:
            point_2 = QgsPoint(fe.geometry().asPoint())

    #print(point_1, point_2)
    wsl.startEditing()
    f = QgsFeature()
    f.setGeometry(QgsGeometry.fromPolyline([point_1, point_2]))
    f.setAttributes([i[0], i[1]])
    pr.addFeature(f)
    wsl.updateExtents()
    wsl.commitChanges()
    