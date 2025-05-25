from datetime import datetime

from flask import Flask, render_template
from flask_htmlmin import HTMLMIN
from flask_pretty import Prettify

from ig5_web import utils, views

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
    return dict(navigation_bar=utils.build_navbar(years), copyright_year=datetime.now().year)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/o_ig5.html")
def about() -> str:
    return views.about(schools, summaries)


@app.route("/<int:order>rocnik.html")
def summary(order) -> str:
    return views.summary(schools, sponsors, summaries, years, order)


@app.route("/statistiky.html")
def stats() -> str:
    return views.stats(schools, summaries)


@app.route("/kontakty.html")
def contacts() -> str:
    return views.contacts(schools)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
