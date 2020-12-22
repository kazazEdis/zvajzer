import requests
import json
import os
from settings import load_env

load_env()
SUDREG_TOKEN = os.getenv("SUDREG_TOKEN")


def provjera(mbs):
    tip_dentifikatora = 'mbs'
    if len(mbs) > 9:
        tip_dentifikatora = 'oib'
    url = "https://sudreg-api.pravosudje.hr/javni/subjekt_detalji?tipIdentifikatora=" + tip_dentifikatora + "&identifikator=" + mbs

    headers = {
        'Ocp-Apim-Subscription-Key': SUDREG_TOKEN
    }

    response = requests.request("GET", url, headers=headers)
    json_object = json.loads(response.content)
    '''
    # Test api response
    json_data = json.dumps(json_object, indent=2)
    print(json_data)
    '''
    if json_object != 'null':
        try:
            tax_number = json_object['potpuni_oib']
            status = json_object['postupci'][0]['vrsta']['znacenje']
            naselje = json_object['sjedista'][0]['naziv_naselja']
            ulica = json_object['sjedista'][0]['ulica'] + ' ' + str(json_object['sjedista'][0].get('kucni_broj', ''))
            try:
                company_name = json_object['skracene_tvrtke'][0]['ime']
            except:
                company_name = json_object['tvrtke'][0]['ime']

            try:
                capital_investment = json_object['temeljni_kapitali'][0]['iznos']
            except:
                capital_investment = None

            return {
                'skraceno_ime_tvrtke': company_name,
                'oib_tvrtke': tax_number,
                'pravni_postupak': status,
                'temeljni_kapital_tvrtke': capital_investment,
                'naselje': naselje,
                'ulica': ulica
            }
        except TypeError:
            return None
