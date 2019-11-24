import numpy
from keras.models import model_from_json
import pandas as pd


# Setup prediction to be ready to recive a request
path = ''
scaling = pd.read_csv(path+"scaling.csv")
scaling = scaling.set_index("feature")

def normalize(df,scaling):
    result = df.copy()
    for feature_name in df.columns:
        max_value = scaling["max"][feature_name]
        min_value = scaling["min"][feature_name]
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    return result

def denormalize(predition,feature_name,scaling):
    max_value = scaling["max"][feature_name]
    min_value = scaling["min"][feature_name]
    return predition*(max_value-min_value)+min_value


# load critic model
json_file = open('critic_model.json', 'r')
loaded_critic_model_json = json_file.read()
json_file.close()
loaded_critic_model = model_from_json(loaded_critic_model_json)
# load weights into critic model
loaded_critic_model.load_weights("critic_model.h5")
print("Loaded critic model from disk")

# load sales model
json_file = open('sales_model.json', 'r')
loaded_sales_model_json = json_file.read()
json_file.close()
loaded_sales_model = model_from_json(loaded_sales_model_json)
# load weights into sales model
loaded_sales_model.load_weights("sales_model.h5")
print("Loaded sales model from disk")


# Get a request
pd_x_critic_score = pd.DataFrame(data=[[12,2006,684704773969,0,28,76]],columns=scaling.index.array) # Numbers from request
pd_x_critic_score = normalize(pd_x_critic_score,scaling)
X_pred_critic_score = pd_x_critic_score.drop("Critic_Score", axis=1).values
X_pred_sales = pd_x_critic_score.drop("Sales", axis=1).values

# Predict a critic score
loaded_critic_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['mae'])
result = loaded_critic_model.predict(X_pred_critic_score)
print("critic score")
print(result)
print(denormalize(result,"Critic_Score",scaling))


# Predict a sale
loaded_sales_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['mae'])
result = loaded_sales_model.predict(X_pred_sales)
print("Sale")
print(result)
print(denormalize(result,"Sales",scaling))
