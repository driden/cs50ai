import cv2
import numpy as np
import os
import sys
import tensorflow as tf
import keras

from numpy.typing import NDArray
from cv2.typing import MatLike

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():
    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test, y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir: str) -> tuple[list[MatLike], list[int]]:
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """

    images: list[MatLike] = []
    labels: list[int] = []
    for cat in range(0, NUM_CATEGORIES):
        dir = f"{data_dir}/{cat}"
        for file in os.listdir(dir):
            filepath = os.path.join(dir, file)
            img = cv2.imread(filepath)

            if img is None:
                print(f"Couldn't load {filepath}", file=sys.stderr)
                sys.exit(1)

            img = cv2.resize(src=img, dsize=(IMG_WIDTH, IMG_HEIGHT))
            images.append(img)
            labels.append(cat)

    return images, labels


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """

    kernel_size = (3, 3)

    filters = 32
    max_pooling = True
    dropout = True
    second_cv_layer = True

    model = keras.models.Sequential()
    model.add(
        keras.layers.Conv2D(
            16 if second_cv_layer else filters,
            kernel_size,
            activation="relu",
            input_shape=(IMG_HEIGHT, IMG_WIDTH, 3),
        )
    )

    if max_pooling:
        model.add(
            # Max-pooling layer, using 2x2 pool size
            keras.layers.MaxPooling2D(pool_size=(2, 2)),
        )

    if second_cv_layer:
        model.add(
            keras.layers.Conv2D(
                filters,
                kernel_size,
                activation="relu",
            )
        )
        if max_pooling:
            model.add(
                # Max-pooling layer, using 2x2 pool size
                keras.layers.MaxPooling2D(pool_size=(2, 2)),
            )

        model.add(
            keras.layers.Conv2D(
                filters * 2,
                kernel_size,
                activation="relu",
            )
        )
        model.add(
            # Max-pooling layer, using 2x2 pool size
            keras.layers.MaxPooling2D(pool_size=(2, 2)),
        )

    model.add(keras.layers.Flatten())
    model.add(
        keras.layers.Dense(128, activation="relu"),
    )

    if dropout:
        model.add(keras.layers.Dropout(0.3))

    model.add(
        keras.layers.Dense(NUM_CATEGORIES, activation="softmax"),
    )

    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )

    print(model.summary())
    return model


if __name__ == "__main__":
    main()
