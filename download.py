import requests
import concurrent.futures
import deduplicate


def download_single_captcha(name: str, dedup: set):
    try:
        response = requests.get('https://app.hakom.hr/captcha.aspx')
        if response.status_code != 200:
            raise Exception(f'Returned status code {response.status_code}')
        shash = deduplicate.hash_binary(response.content)
        if shash in dedup:
            print(f'hash {shash} already present')
            return
        dedup.add(shash)
        with open(name, 'wb') as file:
            file.write(response.content)
    except Exception as e:
        print(e)
        raise e


def download_dataset(path: str, n: int):
    with concurrent.futures.ThreadPoolExecutor(4) as executor:
        futures = []
        dedup = deduplicate.renamed_files_hashes()
        for i in range(n):
            futures.append(executor.submit(
                download_single_captcha, f'{path}/captcha_{i}.jpeg', dedup))
        concurrent.futures.wait(futures)


if __name__ == '__main__':
    download_dataset('./dataset', 10000)
    deduplicate.clean_downloads()
