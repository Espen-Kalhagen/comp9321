from keras.models import model_from_json
import pandas as pd
import tensorflow as tf

#TODO: Worldbank data for gdp
#TODO: platform

class Neuralnet:

    def normalize(self,df,scaling):
        result = df.copy()
        for feature_name in df.columns:
            max_value = scaling["max"][feature_name]
            min_value = scaling["min"][feature_name]
            result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
        return result

    def denormalize(self, predition,feature_name,scaling):
        max_value = scaling["max"][feature_name]
        min_value = scaling["min"][feature_name]
        return abs(predition)*(max_value-min_value)+min_value

    def getRegionNumber(self, region):
        result = self.region_codes.loc[region]
        return result.code.item(0)

    def __init__(self):
        # Setup prediction to be ready to recive a request ---------
        path = './data/'
        self.scaling = pd.read_csv(path+"scaling.csv")
        self.scaling = self.scaling.set_index("feature")
        self.platform_codes = pd.read_csv(path+"platform_codes.csv")
        self.platform_codes = self.platform_codes.set_index("platform")
        self.region_codes = pd.read_csv(path+"region_codes.csv",na_filter = False)
        self.region_codes = self.region_codes.set_index("region")


        #Load neural net models  ------------------------------------
        # load critic model
        json_file = open(path+'critic_model.json', 'r')
        loaded_critic_model_json = json_file.read()
        json_file.close()
        self.loaded_critic_model = model_from_json(loaded_critic_model_json)
        # load weights into critic model
        self.loaded_critic_model.load_weights(path+"critic_model.h5")
        self.critic_graph = tf.get_default_graph()
        self.loaded_critic_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['mae'])
        print("Loaded critic model from disk")

        # load sales model
        json_file = open(path+'sales_model.json', 'r')
        loaded_sales_model_json = json_file.read()
        json_file.close()
        self.loaded_sales_model = model_from_json(loaded_sales_model_json)
        # load weights into sales model
        self.loaded_sales_model.load_weights(path+"sales_model.h5")
        self.sales_graph = tf.get_default_graph()
        self.loaded_sales_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['mae'])
        print("Loaded sales model from disk")

    def predictRating(self, year,region,sales,platform=0,gdp=684704773969):

        region = self.getRegionNumber(region)

        pd_x_critic_score = pd.DataFrame(data=[[platform, int(year), gdp, region, int(sales), 0]],
                                         columns=self.scaling.index.array)
        pd_x_critic_score = self.normalize(pd_x_critic_score, self.scaling)
        X_pred_critic_score = pd_x_critic_score.drop("Critic_Score", axis=1).values

        # Predict a critic score
        with self.critic_graph.as_default():
            result = self.loaded_critic_model.predict(X_pred_critic_score)

        print("critic score")
        result = self.denormalize(result, "Critic_Score", self.scaling)
        return result.item(0)

    def predictSales(self, year,region,rating,platform=0,gdp=684704773969):

        region = self.getRegionNumber(region)

        pd_x_critic_score = pd.DataFrame(data=[[platform, int(year), gdp, region, 0, int(rating)]],
                                         columns=self.scaling.index.array)
        pd_x_critic_score = self.normalize(pd_x_critic_score, self.scaling)
        X_pred_sales = pd_x_critic_score.drop("Sales", axis=1).values

        # Predict a sale
        with self.critic_graph.as_default():
            result = self.loaded_sales_model.predict(X_pred_sales)
        result = self.denormalize(result, "Sales", self.scaling)
        return result.item(0)
