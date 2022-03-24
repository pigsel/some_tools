from pathlib import Path
from qgis.PyQt.QtCore import QVariant

# path to files
p = Path(r'D:\work\_TP\test\vcia\qgis\635')
p_spans = p / 'qgis3.txt'
p_ngab = p / 'qgis2.txt'
p_clines = p / 'qgis1.txt'


def readtxt(pathtofile):
    # read file and save it as list
    strokes = []
    with pathtofile.open() as f:
        for line in f:
            # separate strke by tab ('\t') and delete end of strokes ('\n')
            strokes.append(line.strip('\n').split('\t'))

    return strokes


clines = readtxt(p_clines)   # read clines

# ***
# choose direct layer name
vl = QgsVectorLayer(str(p) + "\\635.gpkg|layername=coords")
pr = vl.dataProvider()

temp_names = []   # to delete dublicates with same id
for i in range(len(clines)):
    if not clines[i][1] in temp_names:
        temp_names.append(clines[i][1])    # add to list to delete if it has dublicates

        # add a feature
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(clines[i][3]), float(clines[i][4]))))
        fet.setAttributes(clines[i])
        pr.addFeatures([fet])

        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        vl.updateExtents()

vl.commitChanges()

# choose direct layer name for cline
vl2 = QgsVectorLayer(str(p) + "\\635.gpkg|layername=cline")
pr = vl2.dataProvider()

cn = clines[0][2]    # cline num = cline num from 1st stroke
points = []   # list of points
for i in range(len(clines)):
    if cn == clines[i][2] and i != (len(clines)-1):
        # if no new cline and not final point
        # collect points
        points.append(QgsPoint(float(clines[i][3]), float(clines[i][4])))

    elif i == (len(clines)-1):
        #if final point - take it to the list
        points.append(QgsPoint(float(clines[i][3]), float(clines[i][4])))
        # add a feature
        fet = QgsFeature()
        #   and save it as cline
        fet.setGeometry(QgsGeometry.fromPolyline(points))
        fet.setAttributes([int(cn)])
        pr.addFeatures([fet])
        vl2.updateExtents()

    else:
        # in case it is first point with new cline
        # add a feature
        fet = QgsFeature()
        # save the list of points
        fet.setGeometry(QgsGeometry.fromPolyline(points))
        fet.setAttributes([int(cn)])
        pr.addFeatures([fet])
        vl2.updateExtents()
        # and start new list
        points = []
        # add first point to the new list
        points.append(QgsPoint(float(clines[i][3]), float(clines[i][4])))
        # change cline number
        cn = clines[i][2]
        

vl2.commitChanges()

# load notgab tab - qgis2.txt
ngtab = readtxt(p_ngab)   # read file
# choose direct layer name
vl3 = QgsVectorLayer(str(p) + "\\635.gpkg|layername=ngtab")
pr = vl3.dataProvider()

for i in range(len(ngtab)):
        # add a feature
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(ngtab[i][3]), float(ngtab[i][4]))))
        fet.setAttributes([i+1] + ngtab[i])   # add i(num) as first column
        pr.addFeatures([fet])

        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        vl3.updateExtents()

vl3.commitChanges()

# add spans
ngspans = readtxt(p_spans)   # read file
vl4 = QgsVectorLayer(str(p) + "\\635.gpkg|layername=spans")
pr = vl4.dataProvider()
for i in range(len(ngspans)):
    p1 = QgsPoint(float(ngspans[i][1]), float(ngspans[i][2]))
    p2 = QgsPoint(float(ngspans[i][4]), float(ngspans[i][5]))
    # add a feature
    fet = QgsFeature()
    #   and save it as cline
    fet.setGeometry(QgsGeometry.fromPolyline([p1, p2]))
    fet.setAttributes([i+1] + ngspans[i])
    pr.addFeatures([fet])
    vl4.updateExtents()

vl4.commitChanges()





