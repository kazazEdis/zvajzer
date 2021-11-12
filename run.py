import os.path
from pathlib import Path

import tensorflow as tf

import model as m

# Batch size for training and validation
batch_size = 16

# Path to the data directory
data_dir = Path("./dataset/")

# Get list of all the images
images = sorted(list(map(str, list(data_dir.glob("*.jpeg")))))

# Maximum length of any captcha in the dataset
max_length = 6

print("Number of images found: ", len(images))

"""
## Create `Dataset` objects
"""

dataset = tf.data.Dataset.from_tensor_slices((images, None))
dataset = (
    dataset.map(m.encode_single_sample, num_parallel_calls=tf.data.AUTOTUNE)
        .batch(batch_size)
        .prefetch(buffer_size=tf.data.AUTOTUNE)
)

model, prediction_model = m.build_model()
model.load_weights('my_model.hdf5')

if __name__ == '__main__':
    # Train the model
    out = prediction_model.predict(dataset)
    out = m.decode_batch_predictions(out, max_length)
    for x, y in zip(images, out):
        if '[UNK]' in y:
            continue
        path = data_dir.joinpath(f'{y}.jpeg')
        if path == x:
            continue
        is_duplicate = os.path.isfile(path)
        i = 2
        while is_duplicate:
            path = data_dir.joinpath(f'{y}_{i}.jpeg')
            is_duplicate = os.path.isfile(path)
            i += 1
        os.rename(x, path)
    # m.show_validation(prediction_model, dataset, max_length)
