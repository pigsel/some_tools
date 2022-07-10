# part 2 - continue of centrostruct
# in this part we use files from first run
# nd we calc azimuth of spans, line angle, structure angle and xarms


import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point, MultiPoint, LineString, MultiLineString
# from centrostruct import xyz_read, report - лучше добавить руками
import csv


# пути
workdir = Path(r'D:\work\2022_makarov\training\ok')

resultdir = workdir / 'result'
tempdir = workdir / 'temp'


