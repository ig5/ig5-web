from flask import render_template

from ig5_web import utils


def create_schools_geojson(schools: dict) -> dict:
    flat_schools = utils.flatten_schools(schools)

    lucenec = {}
    for school in flat_schools:
        if school["city"] == "Lučenec":
            lucenec = school
            break

    lucenec_coordinates = list(reversed(lucenec["coordinates"]))

    features = []
    for school in flat_schools:
        is_lucenec = school == lucenec
        coordinates = list(reversed(school["coordinates"]))

        point_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coordinates,
            },
            "properties": {
                "name": school["name"],
                "city": school["city"],
            },
        }
        features.append(point_feature)

        if not is_lucenec:
            line_string_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [lucenec_coordinates, coordinates],
                },
            }
            features.append(line_string_feature)

    return {"type": "FeatureCollection", "features": features}


def contacts(schools: dict) -> str:
    return render_template(
        "contacts.html",
        schools=schools,
        map={
            "center": schools["mapSettings"]["center"],
            "zoom": schools["mapSettings"]["zoom"],
            "data": create_schools_geojson(schools),
        },
    )
