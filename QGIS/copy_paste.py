#layer = iface.activeLayer()
# or direct layer name
wlayer = QgsVectorLayer("D:/work/2021/max_den_proj/gis/qgis_example.gpkg|layername=cables")
fefe = wlayer.getFeatures()

list_of_cables = []

# собираем возможные варианты в слое Layer
for f in fefe:
    if not f.attribute('Layer') in list_of_cables:
        list_of_cables.append(f.attribute('Layer'))

print(list_of_cables)

attrList = wlayer.fields().toList()   # collect attributes

# теперь для каждого из вариантов собираем features
for i in list_of_cables:
    print(i)
    fea = []   # list of features to collect
    
    # еще раз вызываем исходный слой и собираем для каждой фазы
    fefe = wlayer.getFeatures()
    for fu in fefe:
        if fu.attribute('Layer') == i:
            fea.append(fu)
    print(len(fea))


    # create new layer for lines
    newlay = iface.addVectorLayer("LineString?crs=EPSG:32647", i, "memory")
    data_provider = newlay.dataProvider()
    data_provider.addAttributes(attrList)   # add attributes
    newlay.updateFields()
    
    newlay.startEditing()
    data_provider.addFeatures(fea)   # add features
    newlay.updateExtents()
    newlay.commitChanges()

print('done')