import pandas as pd
import numpy as np



def generation(x):
    # collection of features
    feature_dict = {}

    feature_dict['abs_max_Sales'] = max(np.abs(x['Sales']))
    feature_dict['abs_min_Sales'] = min(np.abs(x['Sales']))
    feature_dict['range_Sales'] = feature_dict['abs_max_Sales'] - feature_dict['abs_min_Sales']
    feature_dict['abs_mean_Sales'] = np.mean(np.abs(x['Sales']))
    return feature_dict



def generate_features():
    file = '/Users/aarushigera/Downloads/DSE/Comp/comp9321/VideoGame_Data.csv'

    video_game_dataframe = pd.read_csv(file)
    video_game_dataframe = video_game_dataframe[['Sales', 'Critic_Score']]

    # get new generated features
    feature_collection = generation(video_game_dataframe)
    result = pd.DataFrame(list(feature_collection.items()), columns= ['feature', 'value'])
    features_generated_json = result.to_json()
    return features_generated_json

