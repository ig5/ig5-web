import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, render_template
from flask_htmlmin import HTMLMIN
from flask_pretty import Prettify

from ig5_web import utils

app = Flask(__name__)
minify_html = True
# minify_page = False
app.config["MINIFY_PAGE"] = minify_html
app.config["PRETTIFY"] = not minify_html
app.jinja_env.add_extension("jinja2.ext.do")
Prettify(app)
HTMLMIN(app)

schools, sponsors, summaries, years = utils.read_data()


@app.context_processor
def inject_variables():
    return dict(
        navigation_bar=utils.build_navbar(years),
        copyright_year=datetime.now().year,
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/o_ig5.html")
def about():
    countries = schools["schools"].keys()
    team_counts = [s["basic"]["teamCount"] for s in summaries.values()]
    return render_template(
        "about.html",
        team_count_min=min(team_counts),
        team_count_max=max(team_counts),
        school_count=len(utils.flatten_schools(schools)),
        country_count=len(countries),
        countries=countries,
        photos=utils.get_photos("about"),
    )


@app.route("/<int:order>rocnik.html")
def summary(order):
    year = years.get(order)
    if year is None:
        abort(404)

    summary = summaries[year]
    photos_dir = os.path.join("summary", year)
    attended_schools = utils.filter_schools_by_year(schools, year)

    route = summary.get("route")
    if route:
        map_ = {
            "center": route["mapSettings"]["center"],
            "zoom": route["mapSettings"]["zoom"],
            "data": utils.create_route_geojson(route),
        }
    else:
        map_ = {
            "center": [0, 0],
            "zoom": 0,
            "data": {},
        }

    sites = {
        tuple(reversed(feature["geometry"]["coordinates"])): feature["properties"]
        for feature in map_["data"].get("features", [])
        if feature["geometry"]["type"] == "Point" and feature["properties"]["type"] == "site"
    }

    distances = []
    elevations = []
    site_distances = []
    site_elevations = []
    elevation_profile_path = Path(__file__).parent / "data" / "elevations" / f"{year}_elevation_profile.json"
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

    map_["elevation_profile"] = [distances, elevations]
    map_["elevation_profile_sites"] = [site_distances, site_elevations]

    return render_template(
        "summary.html",
        order=order,
        year=year,
        summary=summary,
        helper_points_count=utils.get_helper_points_count(summary),
        sponsors=utils.filter_sponsors_by_year(sponsors, year),
        school_count=utils.school_count(attended_schools),
        schools=attended_schools,
        photos=utils.get_photos(photos_dir),
        photos_special=utils.get_photos(os.path.join(photos_dir, "special")),
        docs=utils.get_docs(year),
        map=map_,
    )


@app.route("/statistiky.html")
def stats():
    def per_category_stats(category_key: str) -> dict:
        stats = defaultdict(lambda: {1: [], 2: [], 3: []})

        for year, data in sorted(summaries.items(), key=lambda item: item[0], reverse=True):
            results = data.get("results", {}).get(category_key, [])
            for position, team in enumerate(results, start=1):
                team_parts = team.split(" ")
                school = " ".join(team_parts[:-1])
                if not school:
                    school = team

                stats[school][position].append(year)

        sorted_stats = dict(
            sorted(stats.items(), key=lambda item: (len(item[1][1]), len(item[1][2]), len(item[1][3])), reverse=True)
        )

        return sorted_stats

    def per_school_stats(category_keys: list[str]) -> dict:
        stats = defaultdict(lambda: {1: [], 2: [], 3: []})

        for year, data in sorted(summaries.items(), key=lambda item: item[0], reverse=True):
            for category_key in category_keys:
                results = data.get("results", {}).get(category_key, [])
                for position, team in enumerate(results, start=1):
                    team_parts = team.split(" ")
                    school = " ".join(team_parts[:-1])
                    if not school:
                        school = team

                    stats[school][position].append(year)

        sorted_stats = dict(
            sorted(stats.items(), key=lambda item: (len(item[1][1]), len(item[1][2]), len(item[1][3])), reverse=True)
        )

        return sorted_stats

    def get_organizers_stats():
        organizers = []
        for school in utils.flatten_schools(schools):
            hosted = school.get("hosted", [])
            if hosted:
                organizers.append((f'{school["name"]} {school["city"]}', list(reversed(hosted))))

        organizers.sort(key=lambda school: (len(school[1]), school[1]), reverse=True)
        return organizers

    def get_schools_attendance():
        school_count_to_years = defaultdict(list)
        for year, _ in sorted(summaries.items(), key=lambda item: item[0], reverse=True):
            attended_schools = utils.filter_schools_by_year(schools, year)
            attended_schools = utils.flatten_schools(attended_schools)
            school_count_to_years[len(attended_schools)].append(year)

        attendance = list(sorted(school_count_to_years.items(), key=lambda item: item[0], reverse=True))
        return attendance

    cat1_stats = per_category_stats("category1")
    cat2_stats = per_category_stats("category2")
    total_stats = per_school_stats(["category1", "category2"])

    for country, country_schools in schools["schools"].items():
        schools["schools"][country] = list(
            sorted(country_schools, key=lambda school: len(school["attended"]), reverse=True)
        )

    return render_template(
        "stats.html",
        organizers=get_organizers_stats(),
        schools=schools,
        schools_attendance=get_schools_attendance(),
        cat1_stats=json.dumps(cat1_stats, ensure_ascii=False),
        cat2_stats=json.dumps(cat2_stats, ensure_ascii=False),
        total_stats=json.dumps(total_stats, ensure_ascii=False),
    )


@app.route("/kontakty.html")
def contacts():
    return render_template(
        "contacts.html",
        schools=schools,
        map={
            "center": schools["mapSettings"]["center"],
            "zoom": schools["mapSettings"]["zoom"],
            "data": utils.create_schools_geojson(schools),
        },
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
