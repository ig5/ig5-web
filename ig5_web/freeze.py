from flask_frozen import Freezer

from ig5_web.app import app, years

app.config["SERVER_NAME"] = "stavgeo.sk"
app.config["PREFERRED_URL_SCHEME"] = "https"
freezer = Freezer(app)


@freezer.register_generator
def summary():
    for order in years.keys():
        yield {"order": order}


if __name__ == "__main__":
    freezer.freeze()
    # freezer.run(debug=True, host="0.0.0.0")
