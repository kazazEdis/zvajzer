from main import zvajzer
import simplejson as json
from flask import Flask, jsonify, render_template

app = Flask(__name__)



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/<oib_mbs>", methods=["POST", "GET"])
def user(oib_mbs):
    data = json.loads(zvajzer(oib_mbs), encoding="'UTF-8'")
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
