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

    route = summary.get("route")

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
        map={
            "center": route["mapSettings"]["center"],
            "zoom": route["mapSettings"]["zoom"],
            "data": utils.create_route_geojson(route),
        },
    )


@app.route("/stats.html")
def stats():
    def per_school_stats(category_key: str) -> dict:
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
            sorted(
                stats.items(),
                key=lambda item: (len(item[1][1]), len(item[1][2]), len(item[1][3])),
                # key=lambda item: len(item[1][1]) * 3 + len(item[1][2]) * 2 + len(item[1][3]),
                reverse=True,
            )
        )

        return sorted_stats

    cat1_stats = per_school_stats("category1")
    cat2_stats = per_school_stats("category2")

    return render_template(
        "stats.html",
        years=list(years.values()),
        cat1_stats=json.dumps(cat1_stats, ensure_ascii=False),
        cat2_stats=json.dumps(cat2_stats, ensure_ascii=False),
    )


@app.route("/kontakty.html")
def contacts():
    return render_template(
        "contacts.html",
        schools=schools,
        schools_flattened=utils.flatten_schools(schools),
        map={
            "center": schools["mapSettings"]["center"],
            "zoom": schools["mapSettings"]["zoom"],
            "data": utils.create_schools_geojson(schools),
        },
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
