# "layer" is a QgsVectorLayer instance
layer = iface.activeLayer()
# or direct layer name
#vlayer = QgsVectorLayer("D:/work/GIS/TP/TP21.gpkg|layername=structures_21")
features = layer.getFeatures()

#print ames of attributes
#for field in layer.fields():
#    print(field.name())
print(layer.name())
print(list(layer.fields().names()))

# for multilines
"""
for f in features:
    name = f.attribute('MXLOCATION')
    id = f.attribute('o_id')
    ne = (f'{id}_{name}')
    print(ne)
    geom = f.geometry()
    #print(geom)
    print('parts of attr:', len(geom.asMultiPolyline()))
    li = []
    a = 0
    for a in range(len(geom.asMultiPolyline()[0])):
        li.append([geom.asMultiPolyline()[0][a].x(), geom.asMultiPolyline()[0][a].y()])
    print(len(li))
    print(len(geom.asMultiPolyline()[0]))
    #print(geom.asMultiPolyline()[0][0].x(), geom.asMultiPolyline()[0][0].y())
    #print('x:', geom.asMultiPolyline()[0][0].x())
    #attrs = f.attributes()
    # attrs is a list. It contains all the attribute values of this feature
    #print(attrs)
    #print(f['x'], f['y'])
    # for this test only print the first feature
    break
"""
for f in features:
    geom = f.geometry()
    print(geom)
    print('parts of attr:', len(geom.asMultiPolygon()))
    for part in range(len(geom.asMultiPolygon())):
        print(len(geom.asMultiPolygon()[part]))
    print(len(geom.asMultiPolygon()[0][0]))
    print(geom.asMultiPolygon()[1][0][0].x())
    print(geom.asMultiPolygon()[0][0][0].x(), geom.asMultiPolygon()[0][0][0].y())
