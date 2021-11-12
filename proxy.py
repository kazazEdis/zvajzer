import os
from settings import load_env
import requests
from stem import Signal
from stem.control import Controller

load_env()
TOR_PASS = os.getenv("TOR_PASS")

def get_current_ip():
    session = requests.session()

    # TO Request URL with SOCKS over TOR
    session.proxies = {}
    session.proxies['http']='socks5h://localhost:9051'
    session.proxies['https']='socks5h://localhost:9051'

    try:
        r = session.get('https://ifconfig.me')
    except Exception as e:
        print(str(e))
    else:
        return r.text


def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password=TOR_PASS)
        controller.signal(Signal.NEWNYM)

if __name__ == '__main__':
    print(get_current_ip())