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


clines = readtxt(p_clines)

# create layer with structures and their names
vl = QgsVectorLayer("Point?crs=EPSG:2193", "structures", "memory")
pr = vl.dataProvider()

# add fields
pr.addAttributes([QgsField("work_id", QVariant.Int),
                    QgsField("id", QVariant.String),
                    QgsField("cline_num",  QVariant.Int),
                    QgsField("x", QVariant.Double),
                    QgsField("y", QVariant.Double),
                    QgsField("z", QVariant.Double),
                    ])
vl.updateFields() # tell the vector layer to fetch changes from the provider

for i in range(len(clines)):
    
    # add a feature
    fet = QgsFeature()
    fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(clines[i][3]), float(clines[i][4]))))
    fet.setAttributes(clines[i])
    pr.addFeatures([fet])

    # update layer's extent when new features have been added
    # because change of extent in provider is not propagated to the layer
    vl.updateExtents()




QgsProject.instance().addMapLayer(vl)
