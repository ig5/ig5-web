from datetime import datetime
import json
import os

from ig5_web import constants


def read_data():
    with open(os.path.join(constants.data_dir, "schools.json")) as f:
        # TODO Sort alphabetically and take utf-8 into consideration.
        schools = json.load(f)

    with open(os.path.join(constants.data_dir, "sponsors.json")) as f:
        # TODO Sort alphabetically and take utf-8 into consideration.
        sponsors = json.load(f)

    with open(os.path.join(constants.data_dir, "summaries.json")) as f:
        summaries = json.load(f)

    years = summaries["summaries"].keys()
    return schools, sponsors, summaries, years


def prepare_template_context(years):
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
        summary_img_dir=constants.summary_img_dir,
        copyright_year=datetime.now().year,
    )


def get_photos(year, special=False):
    base_path = os.path.join(constants.summary_photos_dir, year)
    if special:
        base_path = os.path.join(base_path, "special")

    path = os.path.join(base_path, "thumbnails")
    if not os.path.exists(path):
        return []

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

    path = os.path.join(constants.here, "static", "doc")
    for doc in sorted(os.listdir(path)):
        if doc.startswith(year):
            doc_path = os.path.join(path, doc)
            doc_size = os.path.getsize(doc_path)
            doc_size = round(doc_size / 1024 ** 2, 2)
            doc_type = doc.replace(year, "").replace("_", "").split(".")[0]
            docs.append((doc, doc_size, doc_types[doc_type]))
    return docs
