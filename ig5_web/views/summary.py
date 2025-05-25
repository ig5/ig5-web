import json
import os
from pathlib import Path

from flask import abort, render_template

from ig5_web import utils

here = Path(__file__).parent
static_path = here.parent / "static"


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


def get_point_type(point: dict):
    name = point["name"].lower()

    if name == "štart":
        return "start"

    if name == "cieľ":
        return "finish"

    if is_helper_point(point):
        return "helper"

    return "site"


def create_route_geojson(route: dict):
    if not route:
        return ""

    features = []
    line_string_coordinates = []
    for point in route["points"]:
        coordinates = list(reversed(point["coordinates"]))

        point_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coordinates,
            },
            "properties": {
                "type": get_point_type(point),
                "name": point["name"],
                "description": point["description"],
            },
        }
        features.append(point_feature)
        line_string_coordinates.append(coordinates)

    line_string_feature = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": line_string_coordinates,
        },
    }
    features.append(line_string_feature)
    return {"type": "FeatureCollection", "features": features}


def make_elevation_profile_data(map_: dict, year: int) -> dict:
    sites = {
        tuple(reversed(feature["geometry"]["coordinates"])): feature["properties"]
        for feature in map_["data"].get("features", [])
        if feature["geometry"]["type"] == "Point" and feature["properties"]["type"] == "site"
    }

    distances = []
    elevations = []
    site_distances = []
    site_elevations = []
    elevation_profile_path = here.parent / "data" / "elevations" / f"{year}_elevation_profile.json"
    if elevation_profile_path.exists():
        with open(elevation_profile_path, "r") as file_:
            for distance, point_data in json.load(file_).items():
                distance = float(distance)
                distances.append(distance)
                elevations.append(point_data["elevation"])

                point_coordinates = (point_data["lat"], point_data["lon"])
                site = sites.get(point_coordinates)
                if site:
                    site = {**site}
                    site.pop("type")
                    site["elevation"] = point_data["elevation"]
                    site_distances.append(distance)
                    site_elevations.append(site)

    return {
        "elevation_profile": [distances, elevations],
        "elevation_profile_sites": [site_distances, site_elevations],
    }


def make_map_data(route: dict, year: int) -> dict:
    if route:
        map_ = {
            "center": route["mapSettings"]["center"],
            "zoom": route["mapSettings"]["zoom"],
            "data": create_route_geojson(route),
        }
    else:
        map_ = {
            "center": [0, 0],
            "zoom": 0,
            "data": {},
        }

    elevation_profile_data = make_elevation_profile_data(map_, year)
    map_.update(elevation_profile_data)

    return map_


def summary(schools: dict, sponsors: dict, summaries: dict, years: dict, order: int) -> str:
    year = years.get(order)
    if year is None:
        abort(404)

    summary = summaries[year]
    photos_dir = os.path.join("summary", year)
    attended_schools = utils.filter_schools_by_year(schools, year)

    route = summary.get("route")
    map_ = make_map_data(route, year)

    return render_template(
        "summary.html",
        order=order,
        year=year,
        summary=summary,
        helper_points_count=get_helper_points_count(summary),
        sponsors=utils.filter_sponsors_by_year(sponsors, year),
        school_count=utils.school_count(attended_schools),
        schools=attended_schools,
        photos=utils.get_photos(photos_dir),
        photos_special=utils.get_photos(os.path.join(photos_dir, "special")),
        docs=get_docs(year),
        map=map_,
    )
