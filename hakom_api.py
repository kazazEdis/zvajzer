import requests
import random
from time import sleep
from bs4 import BeautifulSoup
from datetime import date
import database
import proxy


def hakom_provjera(contact):
    try:
        contact_number = int(contact)
    except ValueError:
        print(f"Bad contact number: {contact}")
        exit()
    # API Call
    colors = ['zelena', 'crna', 'plava']  # Random colors (Captcha)
    color = random.choice(colors)
    url = "https://www.hakom.hr/default.aspx?id=62"

    payload = '_valid=' + color + '&_validacija=' + color + '&brojTel=385' + str(contact_number) + '&sto=prijenosBroja'
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }

    proxies = {'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'}
    data = requests.request("POST", url, headers=headers, data=payload, proxies=proxies)
    soup = BeautifulSoup(data.text, features="html.parser")  # Format to BeautifulSoup Object
    operator = 'Molimo pokušajte ponovo za 1 minutu...'
    try:
        operator = soup.findChild('td').text.strip()  # Extract operator info
    except AttributeError:
        pass

    while operator == 'Molimo pokušajte ponovo za 1 minutu...':
        print(f'Bad IP: {proxy.get_current_ip()}, Getting new IP!')
        proxy.renew_tor_ip()
        sleep(5)
        data = requests.request("POST", url, headers=headers, data=payload, proxies=proxies)
        soup = BeautifulSoup(data.text, features="html.parser")
        operator = soup.findChild('td').text.strip()

    if operator != 'Molimo pokušajte ponovo za 1 minutu...':
        # Update Database
        try:
            record = database.read({'kontakt': contact})
            operator_history = record['operator_history']
        except TypeError:
            database.create({'kontakt': contact, 'operator_history': []})
            record = database.read({'kontakt': contact})
            operator_history = record['operator_history']

        timestamp = date.today().strftime("%d-%m-%Y")

        # UPDATE OPERATOR HISTORY
        if len(operator_history) <= 1 or operator != operator_history[-1]['operator']:
            database.update({'kontakt': contact},
                            {'$push': {'operator_history': {'operator': operator, 'timestamp': timestamp}}})
            operator_history.append({'operator': operator, 'timestamp': timestamp})

        # if operator is still the same, update timestamp
        elif len(operator_history) >= 2:
            if operator == operator_history[-1]['operator'] and operator_history[-1]['operator'] == operator_history[-2]['operator']:
                database.update({'kontakt': contact}, {'$pop': {'operator_history': -1}})  # remove last item
                database.update({'kontakt': contact},
                                {'$push': {'operator_history': {'operator': operator,
                                                                'timestamp': timestamp}}})
                operator_history.pop(-1)
                operator_history.append({'operator': operator, 'timestamp': timestamp})
        return {'operator': operator,
                'operator_history': operator_history}
