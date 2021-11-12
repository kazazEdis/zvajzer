"""
Title: OCR model for reading Captchas
Author: [A_K_Nain](https://twitter.com/A_K_Nain)
Date created: 2020/06/14
Last modified: 2020/06/26
Description: How to implement an OCR model using CNNs, RNNs and CTC loss.
"""
import math
import string
from pathlib import Path
import os

"""
## Introduction

This example demonstrates a simple OCR model built with the Functional API. Apart from
combining CNN and RNN, it also illustrates how you can instantiate a new layer
and use it as an "Endpoint layer" for implementing CTC loss. For a detailed
guide to layer subclassing, please check out
[this page](https://keras.io/guides/making_new_layers_and_models_via_subclassing/)
in the developer guides.
"""

"""
## Setup
"""

import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

import edit_distance

# Desired image dimensions
img_width = 150
img_height = 40

# Factor by which the image is going to be downsampled
# by the convolutional blocks. We will be using two
# convolution blocks and each block will have
# a pooling layer which downsample the features by a factor of 2.
# Hence total downsampling factor would be 4.
downsample_factor = 16
starting_filters = 32

# characters = string.digits + string.ascii_lowercase
data_dir = Path("./temp_dataset/")

# Get list of all the images
# images = sorted(list(map(str, list(data_dir.glob("*.jpeg")))))
# labels = [img.split(os.path.sep)[-1].split(".jpeg")[0] for img in images]
# characters = sorted(list(set(char for label in labels for char in label)))
characters=['2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

"""
## Preprocessing
"""

# Mapping characters to integers
char_to_num = layers.StringLookup(vocabulary=list(characters), mask_token=None)

# Mapping integers back to original characters
num_to_char = layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(), mask_token=None, invert=True
)


def split_data(images, labels, train_size=0.9, shuffle=True):
    # 1. Get the total size of the dataset
    size = len(images)
    # 2. Make an indices array and shuffle it, if required
    indices = np.arange(size)
    if shuffle:
        np.random.shuffle(indices)
    # 3. Get the size of training samples
    train_samples = int(size * train_size)
    # 4. Split data into training and validation sets
    x_train, y_train = images[indices[:train_samples]], labels[indices[:train_samples]]
    x_valid, y_valid = images[indices[train_samples:]], labels[indices[train_samples:]]
    return x_train, x_valid, y_train, y_valid


def encode_single_sample(img_path, label):
    # 1. Read image
    img = tf.io.read_file(img_path)
    # 2. Decode and convert to grayscale
    img = tf.io.decode_jpeg(img, channels=3)
    img = tf.image.rgb_to_grayscale(img)
    # 3. Convert to float32 in [0, 1] range
    img = tf.image.convert_image_dtype(img, tf.float32)
    # 4. Resize to the desired size
    img = tf.image.resize(img, [img_height, img_width])
    # 5. Transpose the image because we want the time
    # dimension to correspond to the width of the image.
    img = tf.transpose(img, perm=[1, 0, 2])
    # 6. Map the characters in label to numbers
    if label is not None:
        label = char_to_num(tf.strings.unicode_split(label, input_encoding="UTF-8"))
        # 7. Return a dict as our model is expecting two inputs
        return {"image": img, "label": label}
    return {"image": img}




"""
## Model
"""


class CTCLayer(layers.Layer):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.loss_fn = keras.backend.ctc_batch_cost
        self.cer_accumulator = self.add_weight(name="total_cer", initializer="zeros", trainable=False)
        self.wer_accumulator = self.add_weight(name="total_wer", initializer="zeros", trainable=False)
        self.counter = self.add_weight(name="cer_count", initializer="zeros", trainable=False)
        self.total = self.add_weight(name='total', initializer='zeros', trainable=False)
        self.calculator = edit_distance.EditDistanceCalculator(self.cer_accumulator, self.wer_accumulator, self.counter, self.total)
        self.cer = edit_distance.CERMetric(self.calculator)
        self.wer = edit_distance.WERMetric(self.calculator)

    def call(self, y_true, y_pred):
        # Compute the training-time loss value and add it
        # to the layer using `self.add_loss()`.
        batch_len = tf.cast(tf.shape(y_true)[0], dtype="int64")
        input_length = tf.cast(tf.shape(y_pred)[1], dtype="int64")
        label_length = tf.cast(tf.shape(y_true)[1], dtype="int64")

        input_length = input_length * tf.ones(shape=(batch_len, 1), dtype="int64")
        label_length = label_length * tf.ones(shape=(batch_len, 1), dtype="int64")

        loss = self.loss_fn(y_true, y_pred, input_length, label_length)
        self.add_loss(loss)

        # At test time, just return the computed predictions
        self.calculator.update_state(y_true, y_pred)
        return y_pred


def build_model():
    # Inputs to the model
    input_img = layers.Input(
        shape=(img_width, img_height, 1), name="image", dtype="float32"
    )
    labels = layers.Input(name="label", shape=(None,), dtype="float32")

    filters = starting_filters
    x = input_img

    max_passes = round(math.sqrt(downsample_factor))
    for i in range(1, max_passes + 1):
        # First conv block
        x = layers.Conv2D(
            filters,
            (3, 3),
            activation="relu",
            kernel_initializer="he_normal",
            padding="same",
            name=f"Conv{i}",
        )(x)
        x = layers.MaxPooling2D((2, 2), name=f"pool{i}")(x)
        if i < max_passes:
            filters *= 2

    # We have used two max pool with pool size and strides 2.
    # Hence, downsampled feature maps are 4x smaller. The number of
    # filters in the last layer is 64. Reshape accordingly before
    # passing the output to the RNN part of the model
    new_shape = ((img_width // downsample_factor), (img_height // downsample_factor) * filters)
    x = layers.Reshape(target_shape=new_shape, name="reshape")(x)
    x = layers.Dense(64, activation="relu", name="dense1")(x)
    x = layers.Dropout(0.2)(x)

    # RNNs
    x = layers.Bidirectional(layers.GRU(128, return_sequences=True, dropout=0.25))(x)
    x = layers.Bidirectional(layers.GRU(64, return_sequences=True, dropout=0.25))(x)

    # Output layer
    x = layers.Dense(
        len(char_to_num.get_vocabulary()) + 1, activation="softmax", name="dense2"
    )(x)
    pred_y = x

    # Add CTC layer for calculating CTC loss at each step
    output = CTCLayer(name="ctc_loss")(labels, x)

    # Define the model
    model = keras.models.Model(
        inputs=[input_img, labels], outputs=output, name="ocr_model_v1"
    )
    pred_model = keras.models.Model(
        inputs=input_img, outputs=pred_y, name='pred_model'
    )
    # Optimizer
    opt = keras.optimizers.Adam()
    # Compile the model and return
    model.compile(optimizer=opt)
    return model, pred_model


# A utility function to decode the output of the network
def decode_batch_predictions(pred, max_length):
    input_len = np.ones(pred.shape[0]) * pred.shape[1]
    # Use greedy search. For complex tasks, you can use beam search
    results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][
        :, :max_length
    ]
    # Iterate over the results and get back the text
    output_text = []
    for res in results:
        res = tf.strings.reduce_join(num_to_char(res)).numpy().decode("utf-8")
        output_text.append(res)
    return output_text


def show_validation(prediction_model, validation_dataset, max_length):
    #  Let's check results on some validation samples
    for batch in validation_dataset.take(1):
        batch_images = batch["image"]
        batch_labels = batch.get("label", None)

        preds = prediction_model.predict(batch_images)
        pred_texts = decode_batch_predictions(preds, max_length)

        if batch_labels is not None:
            orig_texts = []
            for label in batch_labels:
                label = tf.strings.reduce_join(num_to_char(label)).numpy().decode("utf-8")
                orig_texts.append(label)

        _, ax = plt.subplots(4, 4, figsize=(15, 5))
        for i in range(len(pred_texts)):
            img = (batch_images[i, :, :, 0] * 255).numpy().astype(np.uint8)
            img = img.T
            if batch_labels is not None:
                real = tf.strings.reduce_join(num_to_char(batch_labels[i])).numpy().decode("utf-8")
                title = f"Prediction: {pred_texts[i]}\nReal: {real}"
                ax[i // 4, i % 4].set_title(title, color='green' if pred_texts[i] == real else 'red')
            else:
                title = f"Prediction: {pred_texts[i]}"
                ax[i // 4, i % 4].set_title(title)
            ax[i // 4, i % 4].imshow(img, cmap="gray")
            ax[i // 4, i % 4].axis("off")
    plt.show()
