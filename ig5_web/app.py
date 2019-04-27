import json
import os

from dotenv import load_dotenv
from flask import Flask, render_template


here = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(os.path.dirname(here), ".env"))
with open(os.path.join(here, "static", "schools.json")) as f:
    schools = json.load(f)


app = Flask(__name__)
app.jinja_env.add_extension("jinja2.ext.do")


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/kontakty")
def contacts():
    return render_template(
        "contacts.html",
        schools=schools,
        gmaps_api_key=os.environ["GMAPS_API_KEY"],
    )


if __name__ == "__main__":
    app.run(debug=True)
