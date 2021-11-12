import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

import model as m

# Batch size for training and validation
batch_size = 16

# Path to the data directory
data_dir = Path("./temp_dataset/")

# Get list of all the images
images = sorted(list(map(str, list(data_dir.glob("*.jpeg")))))
labels = [img.split(os.path.sep)[-1].split(".jpeg")[0] for img in images]

# Maximum length of any captcha in the dataset
max_length = max([len(label) for label in labels])

print("Number of images found: ", len(images))
print("Number of labels found: ", len(labels))

EVALUATE = False

"""
## Create `Dataset` objects
"""

if not EVALUATE:
    # Splitting data into training and validation sets
    x_train, x_valid, y_train, y_valid = m.split_data(np.array(images), np.array(labels))

    train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
    train_dataset = (
        train_dataset.map(m.encode_single_sample, num_parallel_calls=tf.data.AUTOTUNE)
        .batch(batch_size)
        .prefetch(buffer_size=tf.data.AUTOTUNE)
    )

    validation_dataset = tf.data.Dataset.from_tensor_slices((x_valid, y_valid))
    validation_dataset = (
        validation_dataset.map(m.encode_single_sample, num_parallel_calls=tf.data.AUTOTUNE)
        .batch(batch_size)
        .prefetch(buffer_size=tf.data.AUTOTUNE)
    )
else:
    validation_dataset = tf.data.Dataset.from_tensor_slices((np.array(images), np.array(labels)))
    validation_dataset = (
        validation_dataset.map(m.encode_single_sample, num_parallel_calls=tf.data.AUTOTUNE)
            .batch(batch_size)
            .prefetch(buffer_size=tf.data.AUTOTUNE)
    )

"""
Visualize the data
"""


# _, ax = plt.subplots(4, 4, figsize=(10, 5))
# for batch in train_dataset.take(1):
#     images = batch["image"]
#     labels = batch["label"]
#     for i in range(batch_size):
#         img = (images[i] * 255).numpy().astype("uint8")
#         label = tf.strings.reduce_join(m.num_to_char(labels[i])).numpy().decode("utf-8")
#         ax[i // 4, i % 4].imshow(img[:, :, 0].T, cmap="gray")
#         ax[i // 4, i % 4].set_title(label)
#         ax[i // 4, i % 4].axis("off")
# plt.show()

epochs = 100
early_stopping_patience = 10
# Add early stopping
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss", patience=early_stopping_patience, restore_best_weights=True
)
model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath='my_model.hdf5',
    save_weights_only=True,
    monitor='val_loss',
    mode='auto',
    save_best_only=True,
)

model, prediction_model = m.build_model()

if __name__ == '__main__':
    if EVALUATE:
        model.load_weights('my_model.hdf5')
        print(model.evaluate(validation_dataset))
    else:
        # Train the model
        history = model.fit(
            train_dataset,
            validation_data=validation_dataset,
            epochs=epochs,
            callbacks=[early_stopping, model_checkpoint_callback],
        )
    m.show_validation(prediction_model, validation_dataset, max_length)
