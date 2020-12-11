# try to deal with dxf files

# пример файла с комментариями
#############################################
#   0               - дальше идет объект
# SECTION           - старт секции
#   2               - тип секции (имя)
# HEADER
#   9               - variable name identifier (только для HEADER)
# $ACADVER          - версия автокада (тег)
#   1               - код группы (тип текст)
# AC1009            - версия автокада (AC1009 = R11 and R12, AC1015 = AutoCAD 2000)
#   9
# $PLINEGEN         - Governs the generation of linetype patterns around the vertices of a 2D polyline:
                    # 1 = Linetype is generated in a continuous pattern around vertices of the polyline
                    # 0 = Each segment of the polyline starts and ends with a dash
#  70               - код группы (Integer values, such as repeat counts, flag bits, or modes)
#      1            - см. выше - полилиния как продолжение
#   9
# $PSLTSCALE         - Controls paper space linetype scaling: 1 = No special linetype scaling
#  70
#      1             - No special linetype scaling
#   9
# $LWDISPLAY         - Controls the display of lineweights on the Model or Layout tab: 0 = Lineweight is not displayed
# 290                - код группы (Boolean flag value)
#      1             - Lineweight is displayed
#   0                - конец секции
# ENDSEC             - конец секции
#   0
# SECTION
#   2
# TABLES
#   0
# TABLE
#   2
# LTYPE
#  70
#      2
#   0
# LTYPE
#   2
# SOLID
#  70
#      0
#   3
# Solid line style
#  72
#     65
#  73
#      0
#  40
# 0.00
#   0
# LTYPE
#   2
# DASHED
#  70
#      0
#   3
# Dashed line style
#  72
#     65
#  73
#      2
#  40
# 1.00
#  49
# 0.60
#  74
#      0
#  49
# -0.40
#  74
#      0
#   0
# ENDTAB
#   0
# TABLE
#   2
# APPID
#  70
#      1
#   0
# APPID
#   2
# ACAD
#  70
#      0
#   0
# ENDTAB
#   0
# ENDSEC
#   0
# SECTION
#   2
# ENTITIES
#   0
# POLYLINE
#   6
# SOLID
#  62
#      6
#  66
#      1
#  70
#    136
#   0
# VERTEX
#  10
# 1877818.25
#  20
# 5818882.95
#  30
# 69.21
#  70
#     32
#   0
# VERTEX
#  10
# 1877818.50
#  20
# 5818883.37
#  30
# 68.90
#  70
#     32
#   0
#####################################
