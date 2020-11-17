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
    json_data = json.dumps(json_object, indent=2)
    if json_data != 'null':
        return {
            'skraceno_ime_tvrtke': json_object['skracene_tvrtke'][0]['ime'],
            'oib_tvrtke': json_object['oib'],
            'pravni_postupak': json_object['postupci'][0]['vrsta']['znacenje'],
            'temeljni_kapital_tvrtke': json_object['temeljni_kapitali'][0]['iznos'],
            'adresa_sjedista_tvrtke': json_object['sjedista'][0]['naziv_naselja'] + ',' +
                json_object['sjedista'][0]['ulica'] + ' ' + str(json_object['sjedista'][0]['kucni_broj'])

        }
    else:
        pass
