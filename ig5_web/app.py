from datetime import datetime
import json
import os

from dotenv import load_dotenv
from flask import abort, Flask, render_template, send_from_directory


here = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(here, "data")
summary_img_dir = os.path.join("img", "summary")
summary_photos_dir = os.path.join(here, "static", summary_img_dir)

with open(os.path.join(data_dir, "schools.json")) as f:
    schools = json.load(f)

with open(os.path.join(data_dir, "sponsors.json")) as f:
    sponsors = json.load(f)

with open(os.path.join(data_dir, "summaries.json")) as f:
    summaries = json.load(f)

load_dotenv(os.path.join(os.path.dirname(here), ".env"))
gmaps_api_key = os.environ["GMAPS_API_KEY"]

years = summaries["summaries"].keys()


app = Flask(__name__)
app.jinja_env.add_extension("jinja2.ext.do")


@app.context_processor
def inject_variables():
    navigation_bar = [
        ("/", "index", "Novinky"),
        ("/kontakty", "contacts", "Kontakty"),
    ]

    results_subnav = []
    for index, year in enumerate(years, 1):
        results_subnav.append(
            (
                f"/vysledky/{year}",
                f"results-{year}",
                f"{index}. ročník &nbsp;<sub>{year}</sub>",
            )
        )
    navigation_bar.insert(1, {"Výsledky": results_subnav})
    return dict(
        navigation_bar=navigation_bar,
        summary_img_dir=summary_img_dir,
        copyright_year=datetime.now().year,
    )


@app.route("/")
def index():
    return render_template("index.html")


def get_photos(year):
    path = os.path.join(summary_photos_dir, str(year), "thumbnails")
    return sorted(os.listdir(path))


def get_docs(year):
    docs = []
    doc_types = {
        "prezent": "Prezentácia",
        "prihlaska": "Prihláška",
        "sprava": "Oficiálna správa",
        "sutaziaci": "Zoznam súťažiacich",
        "otazky_a_ulohy": "Otázky a úlohy",
        "trasa": "Zoznam súradníc stanovísk",
        "zememeric": "Článok z časopisu Zeměměřič",
        "organizacny_statut": "Organizačný štatút IG5",
        "navrh_formy_spoluprace": "Návrh formy spolupráce",
        "10_rokov_IG5_rating": "10 rokov IG5 - rating",
    }

    path = os.path.join(here, "static", "doc")
    for doc in sorted(os.listdir(path)):
        if doc.startswith(year):
            doc_path = os.path.join(path, doc)
            doc_size = os.path.getsize(doc_path)
            doc_size = round(doc_size / 1024 ** 2, 2)
            doc_type = doc.replace(year, "").replace("_", "").split(".")[0]
            docs.append((doc, doc_size, doc_types[doc_type]))
    return docs


@app.route("/vysledky/<string:year>")
def summary(year):
    if year not in years:
        abort(404)

    return render_template(
        "summary.html",
        year=year,
        sponsors=sponsors,
        schools=schools,
        summaries=summaries,
        photos=get_photos(year),
        docs=get_docs(year),
        gmaps_api_key=gmaps_api_key,
    )


@app.route("/vysledky/<path:to_file>")
def summary_static_files_hack(to_file):
    return send_from_directory("", to_file)


@app.route("/kontakty")
def contacts():
    return render_template(
        "contacts.html", schools=schools, gmaps_api_key=gmaps_api_key
    )


if __name__ == "__main__":
    app.run(debug=True)
