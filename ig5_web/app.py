import json
import os
from collections import defaultdict
from datetime import datetime

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
        map_iframe=utils.create_route_map_iframe(summary.get("route")),
    )


# @app.route("/stats.html")
def stats():
    kat1_stats = defaultdict(dict)
    for year, data in summaries.items():
        results = data.get("results", {}).get("category1", [])

        top3 = []
        for position, team in enumerate(results, start=1):
            team_parts = team.split(" ")
            city = " ".join(team_parts[:-1])
            if not city:
                city = team

            kat1_stats[year][position] = city
            top3.append(city)

        # {
        #   label: 'lucenec',
        #   data: [{"x": 1, "y": 2006}, {"x": 2, "y": 2007}],
        # },

    from pprint import pprint

    pprint(kat1_stats)

    dataset = {}
    for year, data in kat1_stats.items():
        for position, city in data.items():
            if city not in dataset:
                dataset[city] = {"label": city, "data": [], "pointRadius": 5}

            dataset[city]["data"].append({"x": position, "y": int(year)})

    pprint(dataset.keys())

    city_colors = {
        "Lučenec": "red",
        "Banská Štiavnica": "violet",
        "Pécs": "grey",
        "Praha": "green",
        "Bratislava": "orange",
        "Žilina": "pink",
        "Letohrad": "black",
        "Brno": "blue",
        "Trenčín": "grey",
    }

    for city, data in dataset.items():
        color = city_colors[city]
        data["backgroundColor"] = color

    return render_template(
        "stats.html",
        years=list(years.values()),
        dataset=json.dumps(list(dataset.values()), ensure_ascii=False),
        # dataset=dataset,
    )


@app.route("/kontakty.html")
def contacts():
    return render_template(
        "contacts.html",
        schools=schools,
        schools_flattened=utils.flatten_schools(schools),
        map_iframe=utils.create_schools_map_iframe(schools),
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
