import os
from main import zvajzer
import simplejson as json
from flask import Flask, jsonify, render_template, make_response
import hakom_api
from flask_sslify import SSLify
import hakom

app = Flask(__name__)
sslify = SSLify(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/oib/<oib_mbs>", methods=["POST", "GET"])
def user(oib_mbs):
    data = json.loads(zvajzer(oib_mbs), encoding="'UTF-8'")
    return make_response(jsonify(data), 200)


@app.route("/operator/<contact_number>", methods=["GET"])
def hackom(contact_number):
    if contact_number[0:3] != "385":
        contact_number = "385" + contact_number
    print(contact_number)
    operator = hakom.operator(contact_number)
    return make_response(jsonify(operator), 200)
    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='localhost', port=port)