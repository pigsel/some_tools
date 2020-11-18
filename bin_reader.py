# terrascan bin file reader

import struct
from pathlib import Path
import numpy as np


# open
p = Path(r'C:\_igor\work\tp\2021\kk\test_\524_wir_16_time_color.bin')
with open(p, "rb") as binary_file:
    bin_data = binary_file.read()

# HEADER
bin_header = struct.unpack('3i4sli3d2i', bin_data[0:56])
# hdr_size = bin_header[0]   # header size
# hdr_version = bin_header[1]   # Version 20020715, 20010712, 20010129 or 970404
# pnt_cnt = bin_header[4]   # Number of points stored
# bin_units = bin_header[5]   # Units per meter = subpermast * uorpersub
# bin_time = bin_header[9]   # 32 bit integer time stamps appended to points
# bin_color = bin_header[10]   # Color values appended to points
head_ind = (bin_header[1], bin_header[9], bin_header[10])  # to choose calc
print(bin_header)

out_header = ['x', 'y', 'z', 'class', 'echo', 'run_f1', 'run_f2', 'flightline', 'intensity', 'time', 'color']


def collect_points(p_len, p_code, tab_size):
    a = 0
    bin_points = np.empty((0, tab_size), dtype=int)   # create empty array for 10 columns with int values
    for point in range(bin_header[4]):   # for each point in file
        aa = 56 + point*p_len
        bb = aa + p_len
        bin_points = np.vstack((bin_points, struct.unpack(p_code, bin_data[aa:bb])))
        a += 1
        print(a)
    return bin_points


# 16 bit
if head_ind == (20020715, 1, 0):
    print(1)
    points = collect_points(24, '3l4b2HI', 10)
    points = np.insert(points, 11, values=0, axis=1)

elif head_ind == (20020715, 0, 1):
    print(2)
    points = collect_points(24, '3l4b2HI', 10)
    points = np.insert(points, 10, values=0, axis=1)

elif head_ind == (20020715, 0, 0):
    print(3)
    points = collect_points(20, '3l4b2H', 9)
    points = np.insert(points, (10, 11), values=0, axis=1)

elif head_ind == (20020715, 1, 1):
    print(4)
    points = collect_points(28, '3l4b2H2I', 11)

# 8 bit
elif head_ind == (20010712, 1, 0):
    points = collect_points(20, '2bH3lI', 7)
    points = points[:, [3, 4, 5, 0, 2, 1, 2, 6]]
    points = np.insert(points, (5, 5, 8), values=0, axis=1)

elif head_ind == (20010712, 0, 0):
    points = collect_points(16, '2bH3l', 6)
    points = points[:, [3, 4, 5, 0, 2, 1, 2]]
    points = np.insert(points, (5, 5, 7, 7), values=0, axis=1)

elif head_ind == (20010712, 1, 1):
    points = collect_points(24, '2bH3l2I', 8)
    points = points[:, [3, 4, 5, 0, 2, 1, 2, 6]]
    points = np.insert(points, (5, 5), values=0, axis=1)

elif head_ind == (20010712, 0, 1):
    points = collect_points(20, '2bH3lI', 7)
    points = points[:, [3, 4, 5, 0, 2, 1, 2, 6]]
    points = np.insert(points, (5, 5, 7), values=0, axis=1)

else:
    points = ['ищи ошибку']

fin_path = Path(r'C:\_igor\work\tp\2021\kk\test_\points.txt')
np.savetxt(fin_path, points, delimiter=" ")


time_k = 0.0002   # in each time stamp unit
coord_k = bin_header[5]   # in each meter

###  to convert intens+echo to two columns - for 8 bit
# a = 16392   # integer intens+echo - 2bits for echo and 14 for intensity
# b = bin(a)[2:].zfill(16)   # convert to bits
# echo = int(b[:2], 2)
# intens = int(b[2:], 2)


# 'x', 'y', 'z', 'class', 'echo', 'run_f1', 'run_f2', 'flightline', 'intensity',
# class, flight, intens+echo, x, y, z, time, color



# TerraScan binary files
#
# Laser points are normally stored in TerraScan binary format which provides a compact way of
# storing laser points and all the information the application can associate with the points.
#
# The information below refers to file formats which were last revised on 12.07.2001 and on
# 15.07.2002. These version dates are stored in the file header. Future versions of TerraScan may
# store laser points into another format but will always recognize and read in the old files.
#
# Current version of TerraScan reads and writes two versions of the binary file format:
#
# • Scan binary 8 bit line - a more compact version which can accommodate flightline numbers
# 0-255. Files with this format have HdrVersion field set to 20010712.
#
# • Scan binary 16 bit line - a slightly bigger version which can accommodate flightline
# numbers 0-65535. Files with this format have HdrVersion field set to 20020715.
#
# See \terra\addon\routines.c for example source code for reading in TerraScan binary files.
#
#
# File organization
#
# TerraScan binary file consists of a file header of 48 bytes and a number of point records. The size
# of the point record is 16 bytes for file version 20010712 and 20 bytes for file version 20020715.
# Each point record may be followed by an optional four byte unsigned integer time stamp and an
# optional four byte RGB color value.
#
# For example, a file containing four laser points and their time stamps using format 20020715
# would consist of:
# • 48 byte header (ScanHdr)
# • 20 byte record for first point (ScanPnt)
# • 4 byte time stamp for first point
# • 20 byte record for second point (ScanPnt)
# • 4 byte time stamp for second point
# • 20 byte record for first three (ScanPnt)
# • 4 byte time stamp for three point
#
#
# Structure definitions
#
# The structure of the file header is:
# typedef struct {
# 	int HdrSize ; // sizeof(ScanHdr)
# 	int HdrVersion ; // Version 20020715, 20010712, 20010129 or 970404
# 	int RecogVal ; // Always 970401
# 	char RecogStr[4]; // CXYZ
# 	long PntCnt ; // Number of points stored
# 	int Units ; // Units per meter = subpermast * uorpersub
# 	double OrgX ; // Coordinate system origin
# 	double OrgY ;
# 	double OrgZ ;
# 	int Time ; // 32 bit integer time stamps appended to points
# 	int Color ; // Color values appended to points
# } ScanHdr ;
#
#
# The structure of a point record for file version 20010712 is:
# typedef struct {
# BYTE Code ; // Classification code 0-255
# BYTE Line ; // Flightline number 0-255
# USHORT EchoInt ; // Intensity bits 0-13, echo bits 14-15
# long X ; // Easting
# long Y ; // Northing
# long Z ; // Elevation
# } ScanRow ;
#
#
# The structure of a point record for file version 20020715 is:
# typedef struct {
# Point3d Pnt ; // Coordinates
# BYTE Code ; // Classification code
# BYTE Echo ; // Echo information
# BYTE Flag ; // Runtime flag (view visibility)
# BYTE Mark ; // Runtime flag
# USHORT Line ; // Flightline number
# USHORT Intensity ; // Intensity value
# } ScanPnt ;
#
#
# Coordinate system
#
# Laser point coordinates are stored as integer values which are relative to an origin point stored in
# the header. To compute user coordinate values X, Y and Z (normally meters), use:
# X = (Pnt.X - Hdr.OrgX) / (double) Hdr.Units ;
# Y = (Pnt.Y - Hdr.OrgY) / (double) Hdr.Units ;
# Z = (Pnt.Z - Hdr.OrgZ) / (double) Hdr.Units ;
#
#
# Time stamps
#
# Time stamps are assumed to be GPS week seconds. The storage format is a 32 bit unsigned integer
# where each integer step is 0.0002 seconds.
#
#
# Echo information
#
# TerraScan uses two bits for storing echo information. The possible values are:
# 0Only echo
# 1First of many echo
# 2Intermediate echo
# 3Last of many echo
