import os
from main import zvajzer
import simplejson as json
from flask import Flask, jsonify, render_template, make_response
from flask_sslify import SSLify
import hakom_api

app = Flask(__name__)
sslify = SSLify(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/<oib_mbs>", methods=["POST", "GET"])
def user(oib_mbs):
    data = json.loads(zvajzer(oib_mbs), encoding="'UTF-8'")
    return make_response(jsonify(data), 200)


@app.route("/operator/<contact_number>", methods=["POST", "GET"])
def hackom(contact_number):
    if len(contact_number) <= 10:
        operator = hakom_api.hakom_provjera(contact_number)
        return operator
    else:
        return contact_number


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)