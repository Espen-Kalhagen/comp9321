import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



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

def normalize(df):
    result = df.copy()
    scaling = pd.DataFrame(index=df.columns,columns=["max","min"])
    for feature_name in df.columns:
        max_value = df[feature_name].max()
        min_value = df[feature_name].min()
        scaling["max"][feature_name] = max_value
        scaling["min"][feature_name] = min_value
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    scaling.index.name = 'feature'
    scaling.to_csv(path+'scaling.csv')
    return result

if __name__ == '__main__':
    file_video_game = 'Video_Games_Sales_as_at_22_Dec_2016.csv'
    file_GDP = 'GDP.csv'
    path = ''

    video_game_dataframe = pd.read_csv(file_video_game)
    GDP_dataframe = pd.read_csv(file_GDP, skiprows= 4)

    video_game_dataframe = video_game_dataframe.drop(['Name', 'Critic_Count', 'User_Score', 'User_Count',
                                                     'Developer', 'Rating', 'Genre', 'Publisher', "Global_Sales"], axis=1)
    #'NA_Sales','EU_Sales','JP_Sales','Other_Sales'

    video_game_dataframe = video_game_dataframe.dropna()
    #Maybe use one-hot encoding instead
    #video_game_dataframe['Genre'] =  video_game_dataframe['Genre'].astype('category').cat.codes
    #video_game_dataframe['Publisher'] =  video_game_dataframe['Publisher'].astype('category').cat.codes



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

    GDP_dataframe = GDP_dataframe.groupby("Continent").mean()
    GDP_dataframe = GDP_dataframe.transpose()
    GDP_dataframe.index = GDP_dataframe.index.astype("float")



    # Create a row for each instance of NA, EU, JP and others to be abel to train on aera as a feature
    video_game_dataframe = video_game_dataframe.join(GDP_dataframe, on='Year_of_Release')

    eu_dataframe = video_game_dataframe.drop(["JP","NA","Others","NA_Sales","JP_Sales","Other_Sales"], axis=1)
    jp_dataframe = video_game_dataframe.drop(["EU", "NA", "Others", "NA_Sales", "EU_Sales", "Other_Sales"], axis=1)
    na_dataframe = video_game_dataframe.drop(["JP", "EU", "Others", "JP_Sales", "EU_Sales", "Other_Sales"], axis=1)
    others_dataframe = video_game_dataframe.drop(["JP", "EU", "NA", "JP_Sales", "EU_Sales", "NA_Sales"], axis=1)

    eu_dataframe = eu_dataframe.rename(columns={"EU": "GDP", "EU_Sales": "Sales"})
    jp_dataframe = jp_dataframe.rename(columns={"JP": "GDP", "JP_Sales": "Sales"})
    na_dataframe = na_dataframe.rename(columns={"NA": "GDP", "NA_Sales": "Sales"})
    others_dataframe = others_dataframe.rename(columns={"Others": "GDP", "Other_Sales": "Sales"})

    eu_dataframe["Region"] = "EU"
    jp_dataframe["Region"] = "JP"
    na_dataframe["Region"] = "NA"
    others_dataframe["Region"] = "Others"

    video_game_dataframe = pd.concat([eu_dataframe,jp_dataframe,na_dataframe,others_dataframe])

    #Rearrange
    video_game_dataframe = video_game_dataframe[["Platform","Year_of_Release","GDP","Region","Sales","Critic_Score"]]

    video_game_dataframe['Platform'] = pd.Categorical(video_game_dataframe["Platform"]).codes
    video_game_dataframe['Region'] = pd.Categorical(video_game_dataframe["Region"]).codes


    video_game_dataframe = normalize(video_game_dataframe)

    video_game_dataframe = video_game_dataframe.dropna()


    video_game_dataframe.to_csv(path + 'VideoGame_Data.csv', index=False)
    print("Preprosessed files")

    #GDP_dataframe.to_csv(path + 'GDP_Data.csv', index=False)

