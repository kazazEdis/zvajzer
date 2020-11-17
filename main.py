import requests
from bs4 import BeautifulSoup
import companywall
import sudreg
import hakom_api
import simplejson as json


def zvajzer(oib_ili_mbs):
    profile_link = companywall.profile_link(oib_ili_mbs)  # Companywall profile address
    html_doc = requests.get('http://www.simple-cw.hr' + profile_link).text  # HTML Request
    soup = BeautifulSoup(html_doc, 'html5lib')  # HTML file
    sudski = sudreg.provjera(oib_ili_mbs)
    osobe = companywall.odgovorne_osobe(soup)
    linkovi = companywall.contact_imgs(soup)
    brojevi = companywall.ocr(linkovi)
    operator = hakom_api.hakom_provjera(brojevi)

    # Konvertiraj sve u dictionary
    converted_to_dict = {"sudski": sudski, "osobe": osobe, "operators": operator}
    json_data = json.dumps(converted_to_dict, ensure_ascii=False, encoding="utf-8", indent=4)
    return json_data
