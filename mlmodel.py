from keras.models import Sequential
from keras.layers import Dense
import numpy
from sklearn import preprocessing
import matplotlib.pyplot as plt
from keras.models import model_from_json



NUM_COLUMNS=5#Num cols -1

# fix random seed for reproducibility
numpy.random.seed(7)

# load pima indians dataset
dataset = numpy.loadtxt("VideoGame_Data.csv", delimiter=",",skiprows=1)
numpy.random.shuffle(dataset)
splitratio = 0.8

''' Allready scaled
min_max_scaler = preprocessing.MinMaxScaler()
dataset = min_max_scaler.fit_transform(dataset)
scaler_params = min_max_scaler.get_params()
print("Scaler params: " + str(scaler_params))
'''

# split into input (X) and output (Y) variables
X_train = dataset[:int(len(dataset)*splitratio),0:NUM_COLUMNS]
X_val = dataset[int(len(dataset)*splitratio):,0:NUM_COLUMNS]
Y_train = dataset[:int(len(dataset)*splitratio),NUM_COLUMNS]
Y_val = dataset[int(len(dataset)*splitratio):,NUM_COLUMNS]

print("xtrain:")
print(X_train)
print("ytrain:")
print(Y_train)

#Create model for critic score
critic_model = Sequential()
critic_model.add(Dense(32, input_dim=NUM_COLUMNS, activation='relu'))
critic_model.add(Dense(32, activation='relu'))
critic_model.add(Dense(32, activation='relu'))
critic_model.add(Dense(32, activation='relu'))
critic_model.add(Dense(1, activation='relu'))

critic_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['mae'])

hist = critic_model.fit(X_train, Y_train, epochs=150, validation_split=0.1)

print(X_val[0])
result = critic_model.predict(X_val[0:1])
print(result)

#Save model
critic_model_json = critic_model.to_json()
with open("critic_model.json", "w") as json_file:
    json_file.write(critic_model_json)
critic_model.save_weights("critic_model.h5")
print("Saved critic_model")

#Create  model for sales

# split into input (X) and output (Y) variables
X_train = numpy.concatenate((dataset[:int(len(dataset)*splitratio),0:NUM_COLUMNS-1],dataset[:int(len(dataset)*splitratio),NUM_COLUMNS-1:NUM_COLUMNS]),axis=1)
X_val = numpy.concatenate((dataset[int(len(dataset)*splitratio):,0:NUM_COLUMNS-1],dataset[int(len(dataset)*splitratio):,NUM_COLUMNS-1:NUM_COLUMNS]),axis=1)
Y_train = dataset[:int(len(dataset)*splitratio),NUM_COLUMNS-1]
Y_val = dataset[int(len(dataset)*splitratio):,NUM_COLUMNS-1]

print("xtrain:")
print(X_train)
print("ytrain:")
print(Y_train)


sales_model = Sequential()
sales_model.add(Dense(32, input_dim=NUM_COLUMNS, activation='relu'))
sales_model.add(Dense(32, activation='relu'))
sales_model.add(Dense(32, activation='relu'))
sales_model.add(Dense(32, activation='relu'))
sales_model.add(Dense(1, activation='relu'))

sales_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['mae'])

hist = sales_model.fit(X_train, Y_train, epochs=150, validation_split=0.1)

print(X_val[0])
result = sales_model.predict(X_val[0:1])
print(result)

#Save model
sales_model_json = sales_model.to_json()
with open("sales_model.json", "w") as json_file:
    json_file.write(sales_model_json)
sales_model.save_weights("sales_model.h5")
print("Saved sales_model")
