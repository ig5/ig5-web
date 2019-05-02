from flask import abort, Flask, render_template

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


@app.route("/<int:order>rocnik.html")
def summary(order):
    year = years.get(order)
    if year is None:
        abort(404)

    attended_schools = utils.filter_schools_by_year(schools, year)
    return render_template(
        "summary.html",
        order=order,
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


@app.route("/kontakty.html")
def contacts():
    return render_template(
        "contacts.html",
        schools=schools,
        schools_flattened=utils.flatten_schools(schools),
        gmaps_api_key=constants.gmaps_api_key,
    )


if __name__ == "__main__":
    app.run(debug=True)
