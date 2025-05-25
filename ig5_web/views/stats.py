import json
from collections import defaultdict

from flask import render_template

from ig5_web import utils


def per_category_stats(summaries: dict, category_key: str) -> dict:
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


def per_school_stats(summaries: dict, category_keys: list[str]) -> dict:
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


def get_hosts_stats(schools: dict) -> dict:
    hosts = []
    for school in utils.flatten_schools(schools):
        hosted = school.get("hosted", [])
        if hosted:
            hosts.append((school["city"], list(reversed(hosted))))

    hosts.sort(key=lambda school: (len(school[1]), school[1]))

    chart_data = []
    for city, years in hosts:
        for year in years:
            chart_data.append({"x": year, "y": city})

    chart_data = list(sorted(chart_data, key=lambda item: item["x"]))
    chart_labels = list(reversed([host[0] for host in hosts]))
    return {"chart_data": chart_data, "chart_labels": chart_labels}


def get_schools_attendance_stats(schools: dict) -> dict:
    attendance = []
    for school in utils.flatten_schools(schools):
        attended = school.get("attended", [])
        if attended:
            attendance.append((school["city"], attended))

    attendance.sort(key=lambda school: (len(school[1]), school[1]))

    all_years = set()
    chart_data = []
    for city, years in attendance:
        all_years.update(years)
        for year in years:
            chart_data.append({"x": year, "y": city})

    chart_data = list(sorted(chart_data, key=lambda item: item["x"]))
    chart_labels_x = list(sorted(all_years))
    chart_labels_y = [host[0] for host in attendance]
    return {"chart_data": chart_data, "chart_labels_x": chart_labels_x, "chart_labels_y": chart_labels_y}


def get_schools_count_stats(summaries: dict, schools: dict) -> dict:
    school_count_to_years = defaultdict(list)
    for year, _ in sorted(summaries.items(), key=lambda item: item[0], reverse=True):
        year = int(year)
        attended_schools = utils.filter_schools_by_year(schools, year)
        attended_schools = utils.flatten_schools(attended_schools)
        school_count_to_years[len(attended_schools)].append(year)

    count = list(sorted(school_count_to_years.items(), key=lambda item: item[0], reverse=True))

    chart_data = []
    for school_count, years in count:
        for year in years:
            chart_data.append({"x": year, "y": school_count})

    chart_data = list(sorted(chart_data, key=lambda item: item["x"]))
    return {"count": count, "chart_data": chart_data}


def stats(schools: dict, summaries: dict) -> str:
    hosts_stats = get_hosts_stats(schools)
    schools_count_stats = get_schools_count_stats(summaries, schools)
    schools_attendance_stats = get_schools_attendance_stats(schools)
    cat1_stats = per_category_stats(summaries, "category1")
    cat2_stats = per_category_stats(summaries, "category2")
    total_stats = per_school_stats(summaries, ["category1", "category2"])

    for index, data in enumerate(schools_attendance_stats["chart_data"]):
        year = str(data["x"])
        city = data["y"]
        city_cat1_stats = cat1_stats.get(city, {})
        city_cat2_stats = cat2_stats.get(city, {})
        schools_attendance_stats["chart_data"][index]["data"] = {
            "cat1": {
                1: year in city_cat1_stats.get(1, []),
                2: year in city_cat1_stats.get(2, []),
                3: year in city_cat1_stats.get(3, []),
            },
            "cat2": {
                1: year in city_cat2_stats.get(1, []),
                2: year in city_cat2_stats.get(2, []),
                3: year in city_cat2_stats.get(3, []),
            },
        }

    for country, country_schools in schools["schools"].items():
        schools["schools"][country] = list(
            sorted(country_schools, key=lambda school: len(school["attended"]), reverse=True)
        )

    return render_template(
        "stats.html",
        hosts_and_school_count_stats={
            "hosts": hosts_stats["chart_data"],
            "hosts_labels": hosts_stats["chart_labels"],
            "school_count": schools_count_stats["chart_data"],
        },
        schools_attendance_stats=json.dumps(schools_attendance_stats, ensure_ascii=False),
        schools=schools,
        cat1_stats=cat1_stats,
        cat2_stats=cat2_stats,
        total_stats=total_stats,
    )
