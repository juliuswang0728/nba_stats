import seaborn as sns
import matplotlib.pyplot as plt
from os import listdir
import pandas as pd
#from matplotlib import cm

def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

def draw_heatmap(data, figure_idx, title):
    #plt.figure(figure_idx)
    ax = sns.heatmap(data.loc[:, 'GP'::], cmap='YlGnBu', cbar=False)
    cbar = ax.figure.colorbar(ax.collections[0], \
    label='max-normalised statistics over all players in the NBA', pad=0.04)
    plt.yticks(rotation=0)
    plt.xticks(rotation=90)
    plt.title(title)
    plt.tight_layout()
    plt.savefig('champions/' + title + '.png', transparent=True, bbox_inches='tight', format='png')
    #plt.show()
    plt.clf()

def draw_fromfiles(directory='champions/'):
    filenames = find_csv_filenames(directory)
    for i, filename in enumerate(filenames, 1):
        team_stats = pd.read_csv(directory + filename, index_col=0)
        team_stats.columns.name = 'Statistics'
        #team_stats.to_csv('123.csv')
        draw_heatmap(team_stats, i, filename[0:-4])
