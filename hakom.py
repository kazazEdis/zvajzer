import requests
import proxy
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
import shutil
from time import sleep
import deduplicate
import tensorflow as tf
import model as m

model, prediction_model = m.build_model()
model.load_weights('my_model.hdf5')

known_captchas 



def ocr():
    dataset = tf.data.Dataset.from_tensor_slices((['test.jpeg'], None))
    dataset = (
        dataset.map(m.encode_single_sample,
                    num_parallel_calls=tf.data.AUTOTUNE)
        .batch(16)  # batch size
        .prefetch(buffer_size=tf.data.AUTOTUNE)
    )

    out = prediction_model.predict(dataset)
    out = m.decode_batch_predictions(out, 6)  # max length = 6

    return out[0]

# phone_number = "385956363898"


def operator(phone_number: str):
    try:
        session = requests.session()
        response = session.get('https://app.hakom.hr/captcha.aspx')
        if response.status_code != 200:
            raise Exception(f'Returned status code {response.status_code}')
        with open('test.jpeg', 'wb') as file:
            file.write(response.content)

        shash = deduplicate.hash_binary(response.content)

        url = "https://app.hakom.hr/default.aspx?id=62&iframe=yes"
        captcha = ocr()
        payload = f'brojTel={phone_number}&cp={captcha}&iframe=yes&sto=prijenosBroja'
        headers = {
            'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }
        proxies = {'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'}
        response = session.request("POST", url, headers=headers, data=payload, proxies=proxies)

        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            results = soup.find_all("td")
            results = [{"Success": True, "Operator": results[0].text,
                        "Broj": results[1].text, "Status": results[2].text}]
            return results

        except Exception:
            status = soup.find(id="brojRez").text
            timeout = "Molimo pokušajte ponovo za 1 minutu..."
            bad_captcha = "Greška, provjerite unos kontrolne vrijednosti"
            if status == bad_captcha:
                    return operator(phone_number)

            elif status == timeout:
                print(f'Bad IP: {proxy.get_current_ip()}, Getting new IP!')
                proxy.renew_tor_ip()
                sleep(5)
                return operator(phone_number)

    except ConnectionError:
        return [{"Success": False, "Reason": "ConnectionError. Are you online!"}]

    except Exception as e:
        return [{"Success": False, "Reason": e}]


if __name__ == '__main__':
    for i in range(50):
        print(operator('38514810301')[0])
        print(i)
