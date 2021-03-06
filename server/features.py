import pandas as pd
import numpy as np
import statistics
from scipy import stats
import warnings



def generation(x):
    # collection of features
    feature_dict = {}
    try:
        feature_dict['abs_max_Sales'] = max(np.abs(x['Sales']))
        feature_dict['abs_min_Sales'] = min(np.abs(x['Sales']))
        feature_dict['range_Sales'] = feature_dict['abs_max_Sales'] - feature_dict['abs_min_Sales']
        feature_dict['abs_mean_Sales'] = np.mean(np.abs(x['Sales']))
        feature_dict['median_Sales'] = statistics.median(x['Sales'])
        feature_dict['abs_std_Sales'] = np.abs(x['Sales']).std()
        feature_dict['skewness_Sales'] = stats.skew(x['Sales'])

        feature_dict['abs_max_Critic_Score'] = max(np.abs(x['Critic_Score']))
        feature_dict['abs_min_Critic_Score'] = min(np.abs(x['Critic_Score']))
        feature_dict['range_Critic_Score'] = feature_dict['abs_max_Critic_Score'] - feature_dict['abs_min_Critic_Score']
        feature_dict['abs_mean_Critic_Score'] = np.mean(np.abs(x['Critic_Score']))
        feature_dict['median_Critic_Score'] = statistics.median(x['Critic_Score'])
        feature_dict['abs_std_Critic_Score'] = np.abs(x['Critic_Score']).std()
        feature_dict['skewness_Critic_Score'] = stats.skew(x['Critic_Score'])
    except:
        print('error handle')
    return feature_dict



def generate_features():
    path = './data/'
    file = 'VideoGame_Data_without_normalisation.csv'
    # ignore by message
    warnings.filterwarnings("ignore", message="")

    video_game_dataframe = pd.read_csv(path+file)
    video_game_dataframe = video_game_dataframe[['Sales', 'Critic_Score']]

    # get new generated features
    feature_collection = generation(video_game_dataframe)
    result = pd.DataFrame(list(feature_collection.items()), columns= ['feature', 'value'])
    features_generated_json = result.to_json()
    return features_generated_json
