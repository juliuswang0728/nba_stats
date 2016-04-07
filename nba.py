# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 09:24:46 2016

@author: Julius
"""
import draw
import crawler
import numpy as np
import pandas as pd

draw.draw_fromfiles('champions/')
#crawler.crawl_nbastats_champ_by_years(np.arange(1991, 2016))
#crawler.crawl_nbastats(1995)
#print OrderedDict()
'''x = pd.read_csv('atlanta-hawks_1990.csv')
best_stats = x.max(axis=0, numeric_only=True).as_matrix()
y = pd.read_csv('brooklyn-nets_1990.csv')
y = y.max(axis=0, numeric_only=True).as_matrix()
best_stats = np.maximum(best_stats, y) # element-wise max
print x.loc[:, 'GP':'AFG%'].divide(best_stats, axis='columns')'''
