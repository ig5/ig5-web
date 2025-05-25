from flask import render_template

from ig5_web import utils


def about(schools: dict, summaries: dict) -> str:
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
