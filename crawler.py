# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 09:24:46 2016

@author: Julius
"""

import numpy as np
import pandas as pd
import urllib2
import math
from fastnumbers import isfloat
from collections import OrderedDict
from bs4 import BeautifulSoup

import re
import sys

teams_abbr = ['atl', 'bkn', 'bos', 'cha', 'chi', 'cle', 'dal', 'den', 'det', \
'gs', 'hou', 'ind', 'lac', 'lal', 'mem', 'mia', 'mil', 'min', 'nop', 'nyk', \
'okc', 'orl', 'phi', 'phx', 'por', 'sac', 'sa', 'tor', 'utah', 'was']
teams_full_name = ['atlanta-hawks', 'brooklyn-nets', 'boston-celtics', 'charlotte-hornets', \
'chicago-bulls', 'cleveland-cavaliers', 'dallas-mavericks', 'denver-nuggets', \
'detroit-pistons', 'golden-state-warriors', 'houston-rockets', 'indiana-pacers', \
'los-angeles-clippers', 'los-angeles-lakers', 'memphis-grizzlies', 'miami-heat', \
'milwaukee-bucks', 'minnesota-timberwolves', 'new-orleans-pelicans', 'new-york-knicks', \
'oklahoma-city-thunder', 'orlando-magic', 'philadelphia-76ers', 'phoenix-suns', \
'portland-trail-blazers', 'sacramento-kings', 'san-antonio-spurs', 'toronto-raptors', \
'utah-jazz', 'washington-wizards']
team_abbr_full = dict(zip(teams_abbr, teams_full_name))
champion_years = np.arange(1991, 2016)
champions = ['chi', 'chi', 'chi', 'hou', 'hou', 'chi', 'chi', 'chi', 'sa', 'lal', 'lal', 'lal', \
'sa', 'det', 'sa', 'mia', 'sa', 'bos', 'lal', 'lal', 'dal', 'mia', 'mia', 'sa', 'gs']
champions = dict(zip(champion_years, champions))

def crawl_nbastats_champ_by_years(years):
    for year in years:
        champion_teamstats = crawl_nbastats_by_year(year=year, champion_team_name=champions[year])
        print '---------' + str(year) + ' Champ: ' + team_abbr_full[champions[year]] + '---------'

        # keep the first 10 rows of players for factor analysis purpose later
        if champion_teamstats.shape[0] >= 10:
            champion_teamstats = champion_teamstats.iloc[0:10]
            print champion_teamstats
            filename = str(year) + '_' + team_abbr_full[champions[year]] + '.csv'
            champion_teamstats.to_csv(filename)
        else:
            print '# of players is less than 10 on year''s champ team!'

def crawl_nbastats_by_year(year, champion_team_name='dal'):
    champion_team_name = team_abbr_full[champion_team_name]
    url_root = 'http://espn.go.com/nba/team/stats/_/name/'
    best_stats = []
    champion_teamstats = pd.DataFrame()
    for team_abbr, team_name in zip(teams_abbr, teams_full_name):
        URL = url_root + team_abbr + '/year/' + str(year) + '/cat/avgMinutes/' + team_name
        print 'parsing ' + URL + ' ...'
        request = urllib2.Request(URL)
        response = urllib2.urlopen(request)
        if response.url != URL:
            print 'no response on this address, redirect to: ', response.url
            continue
        response = response.read()
        soup = BeautifulSoup(response, 'html.parser')

        players = soup.findAll('tr', {'class': re.compile('^player-')})
        stat_labels = soup.findAll('tr', {'class': ['colhead']})
        total_labels = soup.findAll('tr', {'class': ['total']})
        print soup.title.string

        #print '1: ', total_labels[0].select('td')
        #print '2: ', total_labels[1].select('td')

        player_list = []
        player_dict = {}
        team_stats = OrderedDict()  # avoid dict sorting the keys when adding them

        # Initialise 30 statistics for the team
        stats = ['', '']
        stats[0] = stat_labels[0].select('td')   # Table 1: game statistics
        stats[1] = stat_labels[1].select('td')   # Table 2: shooting statistics
        stat_labels = stats
        for stat in stats[0]:
            team_stats[stat.get_text()] = 0.0
        for stat in stats[1]:
            team_stats[stat.get_text()] = 0.0

        numOfPlayer = len(players) / 2
        player_namelist = []
        for i, player in enumerate(players, 0):
            if i == numOfPlayer:
                break
            player_stats = player.findAll('td')
            player_namelist.append(player_stats[0].get_text().encode('ascii', 'ignore'))
        team_stats = pd.DataFrame(np.zeros([numOfPlayer, len(team_stats.keys())]), \
                        index=player_namelist, columns=team_stats.keys())
        team_stats = team_stats.drop('PLAYER', 1)

        for i, player in enumerate(players, 0):
            player_idx = i % numOfPlayer
            j = i / numOfPlayer
            player_stats = player.findAll('td') # iterate over players within a team

            stat = np.zeros(len(player_stats))
            for stat_label, player_stat in zip(stat_labels[j], player_stats):
                x = player_stat.get_text().encode('ascii', 'ignore')
                if isfloat(x) == True:
                    x = float(x)
                    team_stats.set_value(player_namelist[player_idx], stat_label.get_text(), x)

        '''filename = team_name + '_' + str(year) + '.csv'
        print 'saving ' + filename, ' ...'
        team_stats.to_csv(filename)'''

        # only keep track of champion team with specified year
        if team_name == champion_team_name:
            team_stats.index.name = 'Players'
            team_stats.columns.name = 'Statistics'
            champion_teamstats = team_stats

        # keep track of the best of each statistics
        if len(best_stats) == 0:
            best_stats = team_stats.max(axis=0, numeric_only=True).as_matrix()
        else:
            team_stats = team_stats.max(axis=0, numeric_only=True).as_matrix()
            # only take max if all the entries in 'team_stats' are non-nan
            if not np.isnan(team_stats).any():
                best_stats = np.maximum(best_stats, team_stats) # element-wise max

    # normalise the stats by dividing the champion team's stats by the best stats among all teams
    if (not champion_teamstats.empty) and (len(best_stats) != 0):
        champion_teamstats = champion_teamstats.loc[:, 'GP'::].divide(best_stats, axis='columns')

    return champion_teamstats
