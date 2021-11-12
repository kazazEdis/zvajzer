import hashlib
import os


def hash_binary(stream) -> str:
    sha1 = hashlib.sha1()
    sha1.update(stream)
    return sha1.hexdigest()

def renamed_files_hashes():
    renamed = set()
    temp_dataset_dir = os.listdir("./temp_dataset")
    for i in temp_dataset_dir:
        with open(f'temp_dataset/{i}', 'rb') as file:
            shash = hash_binary(file.read())
            renamed.add(shash)
    return renamed

# return hash,captcha pairs of known captchas
def known_captchas():
    renamed = {}
    temp_dataset_dir = os.listdir("./temp_dataset")
    for i in temp_dataset_dir:
        with open(f'temp_dataset/{i}', 'rb') as file:
            shash = hash_binary(file.read())
            renamed[shash]=i.rstrip(".jpeg")
    return renamed

# return hash,captcha pairs of known captchas
def unknown_captchas():
    renamed = {}
    dataset_dir = os.listdir("./dataset")
    for i in dataset_dir:
        with open(f'dataset/{i}', 'rb') as file:
            shash = hash_binary(file.read())
            renamed[shash]=i.rstrip(".jpeg")
    return renamed

def clean_downloads():
    renamed = renamed_files_hashes()

    dataset_dir = os.listdir("./dataset")
    for i in dataset_dir:
        with open(f'dataset/{i}', 'rb') as file:
            shash = hash_binary(file.read())
            if shash in renamed:
                os.remove(f"dataset/{i}")
                print(f'Deleted duplicate file: {i}')

    for filename in dataset_dir:
        if filename in os.listdir("./temp_dataset"):
            os.remove(f"dataset/{filename}")
