#!/usr/bin/env python
# coding: utf-8

# In[72]:


from pathlib import Path
import csv


# In[73]:


p = Path(r'D:\python\some_tools\dxf_test\skb20')
cgtow = p / 'cgtow.txt'
tabs = []   # таблицы по каждой фазе


# запишем лист с координатами опор из файла

# In[74]:


ctw = []
with cgtow.open() as f:
    spam = csv.reader(f, delimiter='\t', skipinitialspace=True)
    for row in spam:
        if not row[1] == '':
            ctw.append(row)
ctw[1][1]


# In[75]:


dxf_files = list(p.glob('40*.dxf'))   # list of dxf files


# создаем функцию парсер dxf

# In[76]:


def dxf_poly_parse(path):
    
    dxf = []   # list to write all data from file
    
    with open(path) as dxf_file:
        for line in dxf_file:
            dxf.append(line.strip())   # write each stroke to list
            
    polylines = []   # empty list for polylines
    line = []   # list for coords of each polyline

    for i in range(len(dxf)):
        if dxf[i] == 'POLYLINE':
            line = []   # list cleaning
        if dxf[i] == 'VERTEX' and dxf[i+1] == '10':
            line.append((float(dxf[i+2]), float(dxf[i+4]), float(dxf[i+6])))
        if dxf[i] == 'SEQEND':
            polylines.append(line)
    
    return polylines


# делаем функцию рассчета расстояния 2д

# In[77]:


def dist(x1, y1, x2, y2):
    """ расчет расстояния """
    return (((x2-x1)**2 + (y2-y1)**2)**(1/2))


# проход по дхф файлам

# In[78]:


mid_points = []   # list for mid points
for file in dxf_files:
    mids = []   # list of mid points for each phase
    phase = file.stem.split('_')[-1]   # name of phase
    polylines = dxf_poly_parse(file)   # calling function to have polylines
    
    for line in range(len(polylines)):
        d1_min = d2_min = 1000000    # fake distance
        id_start = id_end = 'None'   # fake id
 
        st_x = polylines[line][0][0]
        st_y = polylines[line][0][1]
        end_x = polylines[line][-1][0]
        end_y = polylines[line][-1][1]
        
        # finding start and end ID
        for a in range(len(ctw)):
            # calc if one of other structures is closer to the start of polyline
            
            d2 = dist(st_x, st_y, float(ctw[a][1]), float(ctw[a][2]))
            
            if d2 < d1_min:
                d1_min = d2   # rewrite min dist
                id_start = ctw[a][0]   # rewrite id
                
        for b in range(len(ctw)):
            # calc if one of other structures is closer to the end of polyline
            d2 = dist(end_x, end_y, float(ctw[b][1]), float(ctw[b][2]))
            
            if d2 < d2_min:
                d2_min = d2   # rewrite min dist
                id_end = ctw[b][0]   # rewrite id
        
        mid_x = st_x - (st_x-end_x)/2
        mid_y = st_y - (st_y-end_y)/2
        
        # finding mid_z
        cv_num = len(polylines[line])//2   # central vertex number
        
        d_cv_mid = dist(polylines[line][cv_num][0], polylines[line][cv_num][1], mid_x, mid_y)
        d_b_vert = dist(polylines[line][cv_num][0], polylines[line][cv_num][1], polylines[line][cv_num+1][0], polylines[line][cv_num+1][1])
        mid_z = polylines[line][cv_num][2] - ((polylines[line][cv_num][2] - polylines[line][cv_num+1][2])*(d_cv_mid/d_b_vert))
        
        mids.append((phase, id_start, id_end, round(mid_x, 2),  round(mid_y, 2), round(mid_z, 2)))
    mid_points.append(mids)


# In[79]:


import pandas as pd


# In[26]:


import openpyxl


# In[80]:


mp = {}
for tab in mid_points:
    mp[tab[0][0]] = pd.DataFrame(tab, columns=['phase', 'from', 'to', 'x', 'y', 'z'])


# In[81]:


mp['1a']


# In[82]:


# del(mid_points)


# In[83]:


for key in mp.keys():
    mp[key]['span'] = mp[key][['from', 'to']].agg(' - '.join, axis=1)


# In[84]:


mp_ab = mp['1a'].merge(mp['1b'][['span', 'x', 'y', 'z']], left_on='span', right_on='span', suffixes=('_1a', '_1b'))


# In[85]:


mp_ab


# In[86]:


mp_abc = mp_ab.merge(mp['1c'][['span', 'x', 'y', 'z']], left_on='span', right_on='span', suffixes=(False, '_1c'))


# In[87]:


mp_abc = mp_abc.rename(columns={'x': 'x_1c', 'y': 'y_1c', 'z': 'z_1c'})


# In[88]:


mp_abc = mp_abc[['span', 'from', 'to', 'x_1a', 'y_1a', 'z_1a', 'x_1b', 'y_1b', 'z_1b', 'x_1c', 'y_1c', 'z_1c']]


# In[89]:


mp_abc


# In[90]:


def dist3d(x1, y1, z1, x2, y2, z2):
    """ расчет 3d расстояния """
    return round((((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)**(1/2)), 2)


# In[91]:


mp_abc['dist_ab'] = dist3d(mp_abc['x_1a'], mp_abc['y_1a'], mp_abc['z_1a'], mp_abc['x_1b'], mp_abc['y_1b'], mp_abc['z_1b'])


# In[92]:


mp_abc['dist_bc'] = dist3d(mp_abc['x_1b'], mp_abc['y_1b'], mp_abc['z_1b'], mp_abc['x_1c'], mp_abc['y_1c'], mp_abc['z_1c'])


# In[93]:


mp_abc['dist_ac'] = dist3d(mp_abc['x_1a'], mp_abc['y_1a'], mp_abc['z_1a'], mp_abc['x_1c'], mp_abc['y_1c'], mp_abc['z_1c'])


# In[94]:


mp_abc.to_csv(path_or_buf='1a.txt', index=False, columns=['x_1a', 'y_1a', 'z_1a'], sep=' ', header=False)


# In[95]:


mp_abc.to_csv(path_or_buf='1b.txt', index=False, columns=['x_1b', 'y_1b', 'z_1b'], sep=' ', header=False)


# In[96]:


mp_abc.to_csv(path_or_buf='1c.txt', index=False, columns=['x_1c', 'y_1c', 'z_1c'], sep=' ', header=False)


# In[97]:


mp_abc.to_excel("output.xlsx")


# In[ ]:




