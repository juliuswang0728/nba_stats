import matplotlib.pyplot as plt
import seaborn as sns
from os import listdir
import pandas as pd
import numpy as np
from sklearn.decomposition import NMF
from sklearn.manifold import TSNE
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from draw import draw_heatmap

import crawler

#plt.style.use('presentation')
#from matplotlib import cm

def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

def create_player_index(ntotal):
    indices = []
    for i in range(0, ntotal):
        index = 'Player ' + str(i+1)
        '''if not indices: #empty list
            indices = [string]
        else:
            indices = indices.append(string)'''
        indices.append(index)
    return indices

def readcsv_from_directory(directory):
    filenames = find_csv_filenames(directory)
    champions_stats = np.array([])
    df_struct = pd.DataFrame()

    #DROP_STATS_LIST = ['PER', '2PM', '2PA', '2P%', 'AFG%']
    DROP_STATS_LIST = ['PER', 'AFG%']
    for i, filename in enumerate(filenames, 1):
        team_stats = pd.read_csv(directory + filename, index_col=0)
        for drop_stats in DROP_STATS_LIST:
            if drop_stats in team_stats.columns:
                team_stats = team_stats.drop(drop_stats, 1)

        team_stats.columns.name = 'Statistics'
        if df_struct.empty:
            df_struct = pd.DataFrame(data=None, columns=team_stats.columns, \
                                    index=create_player_index(len(team_stats)))
            df_struct.columns.name = 'Statistics'

        team_stats = team_stats.as_matrix()
        mat_shape = np.shape(team_stats)

        team_stats = team_stats.flatten()
        team_stats = team_stats.reshape([1, len(team_stats)])
        if len(champions_stats) == 0:
            champions_stats = team_stats
        else:
            champions_stats = np.append(champions_stats, team_stats, axis=0)

    return champions_stats, df_struct

def do_analysis(directory1='champions/', directory2='non_champions/',alg='nmf'):
    print 'Collecting data...'
    non_champs, df_struct = readcsv_from_directory(directory2)
    champs, df_struct = readcsv_from_directory(directory1)
    all_teamstats = np.concatenate((champs, non_champs), axis=0)
    #n_components = np.int(len(all_teamstats) * 0.10)
    n_components = 5

    print 'Collecting data...finished!'
    print 'Analysing with ' + alg + '...'
    if alg == 'nmf':
        nmf_model = NMF(n_components=n_components, init='random', \
                        alpha=0.25, l1_ratio=0.2, random_state=0)
        nmf_model.fit(champs)
        print 'Analysing with ' + alg + '...finished!'
        print 'Computing secret sauce...'

        champs_sauce = nmf_model.transform(champs)
        non_champs_sauce = nmf_model.transform(non_champs)

        norm_champs_sauce = np.copy(champs_sauce)
        norm_non_champs_sauce = np.copy(non_champs_sauce)

        for i, sauce in enumerate(champs_sauce, 0):
            norm_champs_sauce[i] = sauce / np.sum(sauce) * 100
            print norm_champs_sauce[i]
        #for team in crawler.champions.values
        columns = ['champion model 1 (1991-1993 chi)', 'champion model 2 (2012-2013 mia)', \
        'champion model 3 (2008, bos)', 'champion model 4 (2001-2002, lal)', \
        'champion model 5 (2003, sas)']
        indices = [str(year) + ', ' + team for year, team in crawler.champions.iteritems()]
        title = 'How champion model changes over years'
        sauce = pd.DataFrame(norm_champs_sauce, index=indices, columns=columns)

        ax = sauce.plot(kind='area', stacked=True, title=title, \
        ylim=[0.0, 100.0], colormap='Dark2', grid=True, rot=90)
        plt.xticks(np.arange(len(indices)), indices)

        ax.set_ylabel('Percent (%)')
        ax.set_xlabel('year')
        l = plt.legend(loc='lower left', fancybox=True, frameon=1)
        l.get_frame().set_facecolor([0.9, 0.9, 0.9])
        plt.tight_layout()
        for text in l.get_texts():
            text.set_color([0.4, 0.4, 0.4])
        #plt.savefig('results/repr_changes.png', transparent=True, bbox_inches='tight')
        #ax.margins(0, 0) # Set margins to avoid "whitespace"

        print 'Computing secret sauce...finished!'
        for idx, factor in enumerate(nmf_model.components_, 1):
            comp = factor.reshape(df_struct.shape)
            factor_df = pd.DataFrame(data=comp, columns=df_struct.columns, \
                                            index=df_struct.index)
            #factor_df = factor_df / factor_df.max()
            draw_heatmap(factor_df, idx+10, 'factor'+str(idx))

        print 'Visualising with tsne (1991 - 2015 NBA teams)...'
        tsne_model = TSNE(n_components=2, random_state=0)
        all_team_sauce = tsne_model.fit_transform(np.concatenate((champs_sauce, non_champs_sauce), axis=0))
        fig, ax = plt.subplots()
        ax.plot(all_team_sauce[0:len(champs_sauce), 0], all_team_sauce[0:len(champs_sauce), 1], \
                'ro', alpha=1.0, label='champions', markersize=20)
        ax.plot(all_team_sauce[len(champs_sauce)::, 0], \
                all_team_sauce[len(champs_sauce)::, 1], 'bo', alpha=0.25, label='non-champions', markersize=20)

        for year, x in enumerate(all_team_sauce[0:len(champs), :], 1991):
            ax.annotate(str(year), (x[0]+0.2, x[1]+0.2), color=[0.2, 0.2, 0.2], fontsize=16)
        plt.title('Visualising team (1991-2015) statistics with t-SNE \n')
        plt.legend(fontsize=16)
        #plt.show()
        print 'Visualising with tsne...finished!'

        print 'Visualising with tsne (2015 NBA teams)...'
        filenames = find_csv_filenames(directory2)
        filenames = filenames[-28::]
        for i, name in enumerate(filenames, 0):
            name = name.replace('.csv', '')
            filenames[i] = name.replace('2015_', '')
        fig, ax = plt.subplots()
        ax.plot(all_team_sauce[0:len(champs_sauce), 0], all_team_sauce[0:len(champs_sauce), 1], \
                'ro', alpha=1.0, label='champions')
        start_idx = -28
        ax.plot(all_team_sauce[start_idx::, 0], all_team_sauce[start_idx::, 1], \
                'bo', alpha=0.7, label='2015 NBA teams')
        for year, x in enumerate(all_team_sauce[0:len(champs), :], 1991):
            ax.annotate(str(year), (x[0]+0.1, x[1]+0.1), color=[0.5, 0.5, 0.5])
        for x, name in zip(all_team_sauce[start_idx::, :], filenames):
            ax.annotate(name.rsplit('-', 1)[1], (x[0]+0.1, x[1]+0.1), color=[0.1, 0.1, 0.1])
        plt.title('Visualising team (2015) statistics with t-SNE')
        plt.legend()
        plt.show()
