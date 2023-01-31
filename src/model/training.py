"""Module that handles all the Neural Network training."""

# from data import data as data_utils

# from tensorflow.python.keras.models import Sequential
# from tensorflow.python.keras.layers import Dense
from numpy import loadtxt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense


def train_model():
    """Train the keras model"""

    data = loadtxt("training.csv", delimiter=",")

    # Load data from CSV file

    # Split data into input and output
    X = data[:, :5]
    y = data[:, 6]

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Scale the input data
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Create a neural network with three layers
    model = Sequential()
    model.add(Dense(12, input_dim=5, activation="relu"))
    model.add(Dense(10, activation="relu"))
    model.add(Dense(1, activation="linear"))

    # Compile the model
    model.compile(loss="mean_squared_error", optimizer="adam")

    # Train the model
    model.fit(X_train, y_train, epochs=150, batch_size=34)

    # Evaluate the model on the test data
    test_loss = model.evaluate(X_test, y_test, verbose=0)
    print("Test loss:", test_loss)

    # X = dataset[:,0:6]
    # y = dataset[:,6]
    # model = Sequential()
    # # to work out how many layers will be good the best thing to do is experimentation:

    # # using three layers for now,
    # """ first layer will have 12 nodes
    #     second layer will have 8 nodes
    #     third layer will have  1 node   """

    # model.add(Dense(12, input_shape=(8,), activation="relu"))
    # # using the ReLU activation function as better performance is acheieved using it,
    # # compared to Tanh function or just the sigmoid function.
    # model.add(Dense(8, activation="relu"))
    # model.add(Dense(1, activation="sigmoid"))
    # # compiling the training model.
    # # I am using the 'adam' optimizer (version of gradient descent)

    # model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])

    # model.fit(X, y, epochs=150, batch_size=10)

    # accuracy = model.evaluate(X,y)
    # print("Accuracy: %.2f" % (accuracy*100))

    # # save_model(model)


MODEL_NAME = "test"


def save_model(model):

    pass


if __name__ == "__main__":
    train_model()
