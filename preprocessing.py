import pandas as pd
import numpy as np

def f(row, NA, EU, JP):
    if row['Country Name'] in NA :
        row['Continent'] = 'NA'
    elif row['Country Name'] in EU :
        row['Continent'] = 'EU'
    elif row['Country Name'] in JP :
        row['Continent'] = 'JP'
    else:
        row['Continent'] = 'Others'
    return row

if __name__ == '__main__':
    file_video_game = '/Users/aarushigera/Downloads/data/Video_Games_Sales_as_at_22_Dec_2016.csv'
    file_GDP = '/Users/aarushigera/Downloads/data/GDP.csv'
    path = '/Users/aarushigera/Downloads/data/'

    videogame_dataframe = pd.read_csv(file_video_game)
    GDP_dataframe = pd.read_csv(file_GDP, skiprows= 4)

    video_game_dataframe = videogame_dataframe.drop(['Name','Platform','Critic_Score', 'Critic_Count', 'User_Score', 'User_Count',
                                                     'Developer', 'Rating'], axis=1)
    video_game_dataframe = video_game_dataframe.dropna()

    GDP_dataframe = GDP_dataframe.drop(GDP_dataframe.ix[:, '1960':'1993'].columns, axis = 1)
    GDP_dataframe = GDP_dataframe.dropna(axis=0, subset=GDP_dataframe.ix[:,'1994':'2018'].columns)
    GDP_dataframe = GDP_dataframe.drop(GDP_dataframe.columns[[-1,-2]],axis=1)
    North_America = ['Bermuda', 'Greenland', 'Canada', 'Saint Pierre', 'Miquelon', 'United States']
    European_Union = ['Austria', 'Belgium', 'Bulgaria', 'Croatia','Cyprus', 'Czechia', 'Denmark', 'Estonia', 'Finland', 'France',
                 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands',
                 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'United Kingdom']
    Japan = ['Japan']
    GDP_dataframe['Continent'] = ""
    GDP_dataframe = GDP_dataframe.apply (lambda row: f(row, North_America, European_Union, Japan), axis=1)

    video_game_dataframe.to_csv(path + 'VideoGame_Data.csv')
    GDP_dataframe.to_csv(path + 'GDP_Data.csv')

