"""Module that handles all the Neural Network training."""
import tensorflow
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from numpy import loadtxt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.models import load_model
from app import prem_app



def train_model():
    """Train the keras model"""

    data = loadtxt("training.csv", delimiter=",")

    # Load data from CSV file

    # Split data into input and output
    X = data[:, :6]
    y = data[:, 6]

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Scale the input data
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Create a neural network with three layers
    model = Sequential()
    model.add(Dense(12, input_dim=6, activation="relu"))
    model.add(Dense(10, activation="relu"))
    model.add(Dense(1, activation="linear"))

    # Compile the model
    model.compile(loss="mean_squared_error", optimizer="adam")

    # Train the model
    model.fit(X_train, y_train, epochs=150, batch_size=34, )

    # Evaluate the model on the test data
    test_loss = model.evaluate(X_test, y_test, verbose=0)
    print("Test loss:", test_loss)
    model.save('fpl_predictor.h5')
    return X
  


MODEL_NAME = "test"

if __name__ == '__main__':
    train_model()
