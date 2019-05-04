from datetime import datetime
import os

from dotenv import load_dotenv
from flask import abort, Flask, render_template
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
load_dotenv(os.path.join(os.path.dirname(utils.here), ".env"))
gmaps_api_key = os.environ["GMAPS_API_KEY"]


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

    photos_dir = os.path.join("summary", year)
    attended_schools = utils.filter_schools_by_year(schools, year)
    return render_template(
        "summary.html",
        order=order,
        year=year,
        summary=summaries[year],
        sponsors=utils.filter_sponsors_by_year(sponsors, year),
        school_count=utils.school_count(attended_schools),
        schools=attended_schools,
        photos=utils.get_photos(photos_dir),
        photos_special=utils.get_photos(os.path.join(photos_dir, "special")),
        docs=utils.get_docs(year),
        gmaps_api_key=gmaps_api_key,
    )


@app.route("/kontakty.html")
def contacts():
    return render_template(
        "contacts.html",
        schools=schools,
        schools_flattened=utils.flatten_schools(schools),
        gmaps_api_key=gmaps_api_key,
    )


if __name__ == "__main__":
    app.run(debug=True)
