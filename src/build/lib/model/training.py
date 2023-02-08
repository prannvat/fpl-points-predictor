"""Module that handles all the Neural Network training."""

from src.data import data as data_utils

from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense

def train_model():
    """ Train the keras model """
    dataset = data_utils.get_all_players_stats_for_this_season()
    
    X = dataset[:, 0:5]
    y = dataset[:, 6]
    model = Sequential()
    # to work out how many layers will be good the best thing to do is experimentation:

    # using three layers for now,
    """ first layer will have 12 nodes
        second layer will have 8 nodes
        third layer will have  1 node   """

    model.add(Dense(12, input_shape=(5,), activation="relu"))
    # using the ReLU activation function as better performance is acheieved using it compared to Tanh function or just the sigmoid function.
    model.add(Dense(8, activation="relu"))
    model.add(Dense(1, activation="sigmoid"))
    # compiling the training model.
    # I am using the 'adam' optimizer (version of gradient descent)
    # I am using cross entropy as the loss argument.
    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])

    model.fit(X, y, epochs=150, batch_size=10)

    accuracy = model.predict(y)
    print("Accuracy: %.2f" % (accuracy * 100))



if __name__ == "__main__":
    train_model()