import requests
from bs4 import BeautifulSoup
import companywall
import sudreg
import simplejson as json


def zvajzer(oib_ili_mbs):
    sudski = sudreg.provjera(oib_ili_mbs)
    if sudski is not None:
        profile_link = companywall.profile_link(oib_ili_mbs)  # Companywall profile address
        html_doc = requests.get('http://www.simple-cw.hr' + profile_link).text  # HTML Request
        soup = BeautifulSoup(html_doc, 'lxml')  # HTML file
        web = companywall.website(soup)
        nkd = companywall.nkd(soup)
        osobe = companywall.odgovorne_osobe(soup)
        linkovi = companywall.contact_imgs(soup)
        brojevi = companywall.ocr(linkovi)

        # Konvertiraj sve u dictionary
        converted_to_dict = {"sudski": sudski, "osobe": osobe, "contacts": brojevi, "nkd": nkd, "web": web}
        json_data = json.dumps(converted_to_dict, ensure_ascii=False, encoding="utf-8", indent=4)
        return json_data
    else:
        converted_to_dict = {"sudski": None}
        json_data = json.dumps(converted_to_dict, ensure_ascii=False, encoding="utf-8", indent=4)
        return json_data
