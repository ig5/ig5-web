from flask import abort, Flask, render_template, send_from_directory

from ig5_web import constants
from ig5_web import utils


app = Flask(__name__)
app.jinja_env.add_extension("jinja2.ext.do")
schools, sponsors, summaries, years = utils.read_data()


@app.context_processor
def inject_variables():
    return utils.prepare_template_context(years)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/vysledky/<string:year>")
def summary(year):
    if year not in years:
        abort(404)

    attended_schools = utils.filter_schools_by_year(schools, year)
    return render_template(
        "summary.html",
        year=year,
        summary=summaries[year],
        sponsors=utils.filter_sponsors_by_year(sponsors, year),
        school_count=utils.school_count(attended_schools),
        schools=attended_schools,
        photos=utils.get_photos(year),
        photos_special=utils.get_photos(year, True),
        docs=utils.get_docs(year),
        gmaps_api_key=constants.gmaps_api_key,
    )


@app.route("/vysledky/<path:to_file>")
def summary_static_files_hack(to_file):
    return send_from_directory("", to_file)


@app.route("/kontakty")
def contacts():
    return render_template(
        "contacts.html",
        schools=schools,
        schools_flattened=utils.flatten_schools(schools),
        gmaps_api_key=constants.gmaps_api_key,
    )


if __name__ == "__main__":
    app.run(debug=True)
