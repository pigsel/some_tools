import csv
from pathlib import Path

# path to file
p = Path(r'D:\work\GIS\TP\TP21_wider.prn')

# read file and save it to list
ws = [] # wider spans
with p.open() as f:
    spamreader = csv.reader(f, delimiter=' ', skipinitialspace=True)
    for row in spamreader:
        ws.append(row)

# create layer for lines
wsl = iface.addVectorLayer("LineString?crs=EPSG:2193", "wider_spans", "memory")
# add atributes to the layer
from qgis.PyQt.QtCore import QVariant
pr = wsl.dataProvider()
pr.addAttributes([QgsField("from", QVariant.String),
                  QgsField("to", QVariant.String),
                  QgsField("width", QVariant.Int)])
wsl.updateFields() 

for i in ws:
    point_1 = point_2 = 0
    print(i)
    # searching coordinates in layer
    # layer = iface.activeLayer()
    layer = QgsVectorLayer("D:/work/GIS/TP/TP21.gpkg|layername=structures_21")
    for fe in layer.getFeatures():
        if fe.attribute('Name') == i[0]:
            point_1 = QgsPoint(fe.geometry().asPoint())
        elif fe.attribute('Name') == i[1]:
            point_2 = QgsPoint(fe.geometry().asPoint())
    #print(point_1, point_2)
    wsl.startEditing()
    f = QgsFeature()
    f.setGeometry(QgsGeometry.fromPolyline([point_1, point_2]))
    f.setAttributes([i[0], i[1], int(i[2])])
    pr.addFeature(f)
    wsl.updateExtents()
    wsl.commitChanges()
    



