import itertools
import json
import os
from unicodedata import normalize

from flask import url_for

here = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(here, "static")


def build_navbar(years):
    navigation_bar = [
        (url_for("index"), "index", "Novinky"),
        (url_for("about"), "about", "O IG5"),
        (url_for("contacts"), "contacts", "Kontakty"),
    ]

    results_subnav = []
    for order, year in years.items():
        results_subnav.append(
            (
                url_for("summary", order=order),
                f"results-{year}",
                f"{year} | {order}. ročník",
            )
        )

    results_subnav = list(reversed(results_subnav))
    results_subnav.insert(0, (url_for("stats"), "results-stats", "Štatistiky"))
    navigation_bar.insert(2, {"Výsledky IG5": results_subnav})

    return navigation_bar


def to_ascii(string):
    normalized = normalize("NFKD", string).encode("ASCII", "ignore")
    return normalized.decode("utf-8").lower()


def inplace_list_of_dicts_sort(list_of_dicts, key):
    for item in list_of_dicts:
        item["normalized_name"] = to_ascii(item[key])
    list_of_dicts.sort(key=lambda x: x["normalized_name"])


def read_data():
    data_dir = os.path.join(here, "data")

    with open(os.path.join(data_dir, "schools.json")) as f:
        schools = json.load(f)
        for country, country_schools in schools["schools"].items():
            inplace_list_of_dicts_sort(country_schools, "city")

    with open(os.path.join(data_dir, "sponsors.json")) as f:
        sponsors = json.load(f)
        inplace_list_of_dicts_sort(sponsors, "name")

    summaries = {}
    for summary_file in sorted(os.listdir(os.path.join(data_dir, "summary"))):
        with open(os.path.join(data_dir, "summary", summary_file)) as f:
            year = summary_file.split(".")[0]
            summaries[year] = json.load(f)

    years = {order: year for order, year in enumerate(summaries.keys(), start=1)}
    return schools, sponsors, summaries, years


def filter_sponsors_by_year(sponsors, year):
    year = int(year)
    return [sponsor for sponsor in sponsors if year in sponsor["supported"]]


def filter_schools_by_year(schools, year):
    year = int(year)
    filtered_schools = {}

    for country, country_schools in schools["schools"].items():
        filtered_country_schools = []

        for school in country_schools:
            if year in school["attended"]:
                filtered_country_schools.append(school)

        if filtered_country_schools:
            filtered_schools[country] = filtered_country_schools

    return {"schools": filtered_schools}


def flatten_schools(schools):
    return list(itertools.chain.from_iterable(schools["schools"].values()))


def school_count(schools):
    return len(flatten_schools(schools))


def get_photos(photos_dir):
    photos_dir = os.path.join("img", photos_dir)

    thumbnails_path = os.path.join(static_path, photos_dir, "thumbnails")
    if not os.path.exists(thumbnails_path):
        return []

    names = sorted(os.listdir(thumbnails_path))
    thumbnails = []
    images = []
    for name in names:
        thumbnails.append(os.path.join(photos_dir, "thumbnails", name))
        images.append(os.path.join(photos_dir, "images", name))

    return list(zip(names, thumbnails, images))
