import requests
import json


def provjera(mbs):
    tip_dentifikatora = 'mbs'
    if len(mbs) > 9:
        tip_dentifikatora = 'oib'
    url = "https://sudreg-api.pravosudje.hr/javni/subjekt_detalji?tipIdentifikatora=" + tip_dentifikatora + "&identifikator=" + mbs

    headers = {
        'Ocp-Apim-Subscription-Key': '2c5e5e5e44bd4231a1bf755ea5a1a592'
    }

    response = requests.request("GET", url, headers=headers)
    json_object = json.loads(response.content)
    '''
    json_data = json.dumps(json_object, indent=2)
    print(json_data)
    '''
    if json_object != 'null':
        try:
            tax_number = json_object['oib']
            status = json_object['postupci'][0]['vrsta']['znacenje']
            address = json_object['sjedista'][0]['naziv_naselja'] + ',' + json_object['sjedista'][0]['ulica'] + ' ' + str(json_object['sjedista'][0].get('kucni_broj', ''))
'
            try:
                company_name = json_object['skracene_tvrtke'][0]['ime']
            except KeyError:
                company_name = json_object['tvrtke'][0]['ime']

            try:
                capital_investment = json_object['temeljni_kapitali'][0]['iznos']
            except KeyError:
                capital_investment = None

            return {
                'skraceno_ime_tvrtke': company_name,
                'oib_tvrtke': tax_number,
                'pravni_postupak': status,
                'temeljni_kapital_tvrtke': capital_investment,
                'adresa_sjedista_tvrtke': address
            }
        except TypeError:
            return None
