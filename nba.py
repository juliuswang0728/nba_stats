# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 09:24:46 2016

@author: Julius
"""
import draw
import crawler
import analysis
import numpy as np
import pandas as pd

def main():
    #draw.draw_fromfiles('champions/')
    analysis.do_analysis(directory1='champions/', directory2='non_champions/')
    #crawler.crawl_nbastats_champ_by_years(np.arange(1996, 2016))
    #crawler.crawl_nbastats(1995)
    #print OrderedDict()
    '''x = pd.read_csv('atlanta-hawks_1990.csv')
    best_stats = x.max(axis=0, numeric_only=True).as_matrix()
    y = pd.read_csv('brooklyn-nets_1990.csv')
    y = y.max(axis=0, numeric_only=True).as_matrix()
    best_stats = np.maximum(best_stats, y) # element-wise max
    print x.loc[:, 'GP':'AFG%'].divide(best_stats, axis='columns')'''

if __name__== "__main__":
    main()
