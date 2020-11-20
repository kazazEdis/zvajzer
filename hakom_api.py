import http.client
import random
import urllib.parse
import urllib.error
from time import sleep
from bs4 import BeautifulSoup


def hakom_provjera(contact):
    contact_number = contact.lstrip('0')
    # API Call
    headers = {
        'sec-ch-ua': '"Chromium";v="86", "\"Not\\A;Brand";v="99", "Google Chrome";v="86"',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://www.hakom.hr',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }

    colors = ['zelena', 'crna', 'plava']  # Random colors (Captcha)
    color = random.choice(colors)

    body = urllib.parse.urlencode({
        '_valid': color,
        '_validacija': color,
        'brojTel': '385' + str(contact_number),
        'sto': 'prijenosBroja',
    })

    conn = http.client.HTTPSConnection('www.hakom.hr')  # Initiate connection
    conn.request("GET", "https://www.hakom.hr/default.aspx?id=62", body, headers)  # Send API request
    data = conn.getresponse()  # Save API response
    soup = BeautifulSoup(data, features="html.parser", from_encoding='utf-8')  # Format to BeautifulSoup Object
    result = soup.findChild('td').text.strip()  # Extract operator info
    if result == 'Molimo pokušajte ponovo za 1 minutu...':
        while result == 'Molimo pokušajte ponovo za 1 minutu...':
            print('Loading...')
            sleep(60)
            conn.request("POST", "https://www.hakom.hr/default.aspx?id=62", body, headers)  # Send API request
            data = conn.getresponse()  # Save API response
            soup = BeautifulSoup(data, features="html.parser", from_encoding='utf-8')  # Format to BeautifulSoup Object
            try:
                result = soup.findChild('td').text.strip()  # Extract operator info
            except AttributeError:
                pass
    print({str('0' + contact_number): result})
    return {str('0' + contact_number): result}
