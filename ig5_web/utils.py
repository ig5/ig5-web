import itertools
import json
import os
from unicodedata import normalize

from flask import url_for
from folium import FeatureGroup, Icon, LayerControl, Map, Marker, PolyLine, Popup

from ig5_web.constants import MAP_POLY_LINE_COLOR, MapMarkerColors, MapMarkerIcons

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
    navigation_bar.insert(2, {"Výsledky IG5": reversed(results_subnav)})

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


def get_docs(year):
    docs = []
    doc_types = {
        "prezent": "Prezentácia",
        "prihlaska": "Prihláška",
        "sprava": "Oficiálna správa",
        "sutaziaci": "Zoznam súťažiacich",
        "otazky_a_ulohy": "Otázky a úlohy",
        "trasa": "Zoznam súradníc stanovísk",
        "vysledky": "Celkové výsledky",
        "zememeric": "Článok z časopisu Zeměměřič",
        "organizacny_statut": "Organizačný štatút IG5",
        "navrh_formy_spoluprace": "Návrh formy spolupráce",
        "10_rokov_IG5_rating": "10 rokov IG5 - rating",
    }

    path = os.path.join(static_path, "doc")
    for doc in sorted(os.listdir(path)):
        if doc.startswith(year):
            doc_path = os.path.join(path, doc)
            doc_size = os.path.getsize(doc_path)
            doc_size = round(doc_size / 1024**2, 2)
            doc_type = doc.replace(year, "").replace("_", "").split(".")[0]
            docs.append((doc, doc_size, doc_types[doc_type]))
    return docs


def is_helper_point(point: dict):
    name = point["name"].lower()

    if not name or "orientačné" in name:
        return True

    return False


def get_helper_points_count(summary: dict) -> int:
    return len([p for p in summary.get("route", {}).get("points", []) if is_helper_point(p)])


def get_marker_color(point: dict) -> str:
    name = point["name"].lower()

    if name in ("štart", "cieľ"):
        return MapMarkerColors.RED

    if is_helper_point(point):
        return MapMarkerColors.LIGHT_GRAY

    return MapMarkerColors.DARKBLUE


def get_marker_icon(point: dict):
    name = point["name"].lower()

    if name == "štart":
        return MapMarkerIcons.PLAY

    if name == "cieľ":
        return MapMarkerIcons.STOP

    if is_helper_point(point):
        return ""

    return MapMarkerIcons.RECORD


def format_coordinates(coordinates):
    return f"N {coordinates[0]}° &nbsp&nbsp E {coordinates[1]}°"


def init_map(map_settings: dict):
    map_ = Map(location=map_settings["center"], zoom_start=map_settings["zoom"])
    map_.get_root().width = "100%"
    map_.get_root().height = "550px"
    return map_


def create_route_map_iframe(route: dict):
    if not route:
        return ""

    map_ = init_map(route["mapSettings"])

    markers_main = FeatureGroup(name="Stanoviská", control=False).add_to(map_)
    markers_helper = FeatureGroup(name="Orientačné body", show=False).add_to(map_)

    points = []
    for point in route["points"]:
        coordinates = point["coordinates"]
        coordinates_str = format_coordinates(coordinates)
        points.append(coordinates)

        if point["name"] and point["description"]:
            text = f'{point["name"]}: {point["description"]}<br>{coordinates_str}'
        else:
            text = ""

        if is_helper_point(point):
            opacity = 0.7
        else:
            opacity = 1

        marker = Marker(
            location=coordinates,
            popup=Popup(text or coordinates_str, min_width=250, max_width=500),
            icon=Icon(color=get_marker_color(point), icon=get_marker_icon(point)),
            opacity=opacity,
        )

        if is_helper_point(point):
            markers_helper.add_child(marker)
        else:
            markers_main.add_child(marker)

    PolyLine(points, color=MAP_POLY_LINE_COLOR, weight=5).add_to(map_)
    LayerControl().add_to(map_)

    iframe = map_.get_root()._repr_html_()
    return iframe


def create_schools_map_iframe(schools: dict):
    map_ = init_map(schools["mapSettings"])

    flat_schools = flatten_schools(schools)

    lucenec = {}
    for school in flat_schools:
        if school["city"] == "Lučenec":
            lucenec = school
            break

    for school in flat_schools:
        is_lucenec = school == lucenec
        coordinates = school["coordinates"]

        name_and_city = f'{school["name"]}, {school["city"]}'
        text = f"{name_and_city}<br>{format_coordinates(coordinates)}"
        icon_color = MapMarkerColors.RED if is_lucenec else MapMarkerColors.DARKBLUE

        Marker(
            location=coordinates,
            popup=Popup(text, min_width=250, max_width=500),
            icon=Icon(color=icon_color, icon=MapMarkerIcons.RECORD),
        ).add_to(map_)

        if not is_lucenec:
            points = [lucenec["coordinates"], coordinates]
            PolyLine(points, color=MAP_POLY_LINE_COLOR, weight=3).add_to(map_)

    iframe = map_.get_root()._repr_html_()
    return iframe
