import requests
from bs4 import BeautifulSoup
import os
import companywall
import sudreg
import hakom_api
import simplejson as json
from flask import Flask, jsonify, send_from_directory, request

app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'static/favicon.ico', mimetype='image/vnd.microsoft.icon')


def main(oib_ili_mbs):
    profile_link = companywall.profile_link(oib_ili_mbs)  # Adresa Companywall profila
    html_doc = requests.get('http://www.simple-cw.hr' + profile_link).text  # HTML Zahtjev
    soup = BeautifulSoup(html_doc, 'html5lib')  # HTML datoteka
    sudski = sudreg.provjera(oib_ili_mbs)
    osobe = companywall.odgovorne_osobe(soup)
    linkovi = companywall.contact_imgs(soup)
    brojevi = companywall.ocr(linkovi)
    operator = hakom_api.hakom_provjera(brojevi)

    # Konvertiraj sve u dictionary
    converted_to_dict = {"sudski": sudski, "osobe": osobe, "operators":operator}
    json_data = json.dumps(converted_to_dict, ensure_ascii=False, encoding="utf-8", indent=4)
    return json_data


@app.route("/<oib_mbs>", methods=["POST", "GET"])
def user(oib_mbs):
    data = json.loads(main(oib_mbs), encoding="'UTF-8'")
    return jsonify(data)


@app.route('/api/v1/list', methods=['POST'])
def index():
    if request.method == 'POST':
        data = request.get_json()
        oib = data["oib"]
        img_url_list = data["brojevi"]
        brojevi_telefona = companywall.ocr(img_url_list)
        return jsonify(brojevi_telefona)


if __name__ == "__main__":
    app.run(debug=True)
