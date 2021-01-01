import requests
from bs4 import BeautifulSoup
import companywall
import sudreg
import database
import simplejson as json



def zvajzer(oib_ili_mbs):
    sudski = sudreg.provjera(oib_ili_mbs)
    mongoDB = database.company(oib_ili_mbs)
    if sudski is not None:
        profile_link = companywall.profile_link(sudski['oib_tvrtke'])  # Companywall profile address
        html_doc = requests.get('http://www.simple-cw.hr' + profile_link).text  # HTML Request
        soup = BeautifulSoup(html_doc, 'lxml')  # HTML file
        web = companywall.website(soup)
        nkd = companywall.nkd(soup)
        velicina = companywall.size(soup)
        osobe = companywall.odgovorne_osobe(soup)

        try:
            brojevi = mongoDB['kontakti']
        except TypeError:
            brojevi = []

        if len(brojevi) == 0:
            linkovi = companywall.contact_imgs(soup)
            brojevi = companywall.ocr(linkovi)

        # Konvertiraj sve u dictionary
        converted_to_dict = {
            "_id": sudski["oib_tvrtke"],
            "skraceno_ime_tvrtke": sudski["skraceno_ime_tvrtke"],
            "pravni_postupak": sudski["pravni_postupak"],
            "temeljni_kapital_tvrtke": sudski["temeljni_kapital_tvrtke"],
            "velicina": velicina,
            "nkd": nkd,
            "naselje": sudski["naselje"],
            "ulica": sudski["ulica"],
            "web": web,
            "osobe": osobe,
            "kontakti": brojevi
        }

        if mongoDB == None:
            database.new_company(converted_to_dict)

        json_data = json.dumps(converted_to_dict, ensure_ascii=False, encoding="utf-8", indent=4)
        return json_data
    else:
        converted_to_dict = {"_id": None}
        json_data = json.dumps(converted_to_dict, ensure_ascii=False, encoding="utf-8", indent=4)
        return json_data