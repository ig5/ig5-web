import json
import time
from pathlib import Path

import requests
from geopy.distance import geodesic
from shapely.geometry import LineString, Point


def get_route_opentopodata_locations(summary_path: Path) -> str:
    with open(summary_path, "r", encoding="utf-8") as file:
        summary = json.load(file)

    route_points = []
    route = summary.get("route")
    if not route:
        return ""

    for point in route["points"]:
        coordinates = f'{point["coordinates"][0]},{point["coordinates"][1]}'
        route_points.append(coordinates)

    return "|".join(route_points)


def get_route_elevation_data(locations: str, save_to_path: Path, extra_params: dict | None = None) -> None:
    params = {"locations": locations}
    if extra_params:
        params.update(extra_params)

    # https://www.opentopodata.org/api/
    url = "https://api.opentopodata.org/v1/eudem25m"
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data from Open Topo Data API: {response.status_code}")

    data = response.json()
    with open(save_to_path, "w", encoding="utf-8") as file_handle:
        json.dump(data, file_handle, ensure_ascii=False, indent=2)


def get_routes_elevation_data():
    summary_dir = Path(__file__).parent.parent / "ig5_web" / "data" / "summary"
    summary_files = sorted(summary_dir.glob("*.json"))

    for summary_file in summary_files:
        summary_path = summary_file.resolve()
        year = summary_path.stem

        locations = get_route_opentopodata_locations(summary_path)
        if not locations:
            print(f"No route found for {year}. Skipping...")
            continue

        save_to_path = Path(__file__).parent.parent / "ig5_web" / "data" / "elevations" / f"{year}.json"
        if not save_to_path.exists():
            get_route_elevation_data(locations, save_to_path)
            time.sleep(1)

        save_to_path = Path(__file__).parent.parent / "ig5_web" / "data" / "elevations" / f"{year}_sampled.json"
        if not save_to_path.exists():
            get_route_elevation_data(locations, save_to_path, {"samples": 100})
            time.sleep(1)


def sort_exact_and_sampled_elevations(
    route_points_path: Path, sampled_points_path: Path
) -> tuple[list[tuple[float, float]], dict[tuple[float, float], float]]:
    # Load the JSON files
    with open(route_points_path, "r", encoding="utf-8") as file:
        route_points_data = json.load(file)

    with open(sampled_points_path, "r", encoding="utf-8") as file:
        sampled_points_data = json.load(file)

    route_points = []
    route_points_elevations = {}
    for result in route_points_data["results"]:
        lat = result["location"]["lat"]
        lng = result["location"]["lng"]
        elevation = result["elevation"]
        route_points.append([lat, lng])
        route_points_elevations[lat, lng] = elevation

    sampled_points = []
    sampled_points_elevations = {}
    for result in sampled_points_data["results"]:
        lat = result["location"]["lat"]
        lng = result["location"]["lng"]
        elevation = result["elevation"]
        sampled_points.append([lat, lng])
        sampled_points_elevations[lat, lng] = elevation

    line = LineString(route_points)
    original_shapely_points = [Point(xy) for xy in route_points]
    sampled_shapely_points = [Point(xy) for xy in sampled_points]

    # Combine and sort all by distance along the line
    all_shapely_points = original_shapely_points + sampled_shapely_points
    all_shapely_points_sorted = list(sorted(set(all_shapely_points), key=lambda pt: line.project(pt)))
    all_points_sorted = [(point.x, point.y) for point in all_shapely_points_sorted]
    all_points_elevations = {**route_points_elevations, **sampled_points_elevations}
    return all_points_sorted, all_points_elevations


def make_elevation_profile(
    all_points_sorted: list[tuple[float, float]], all_points_elevations: dict[tuple[float, float], float]
) -> dict[float, dict[str, float]]:
    points = []
    for point in all_points_sorted:
        lat, lon = point
        elevation = all_points_elevations[lat, lon]
        if elevation is not None:
            points.append([lat, lon, elevation])

    distances = [0]
    for i in range(1, len(all_points_sorted)):
        previous_point = points[i - 1][:-1]
        current_point = points[i][:-1]
        distance = geodesic(previous_point, current_point).meters
        distances.append(distances[-1] + distance)

    return {
        round(distance, 2): {"lat": point[0], "lon": point[1], "elevation": round(point[2], 2)}
        for (distance, point) in list(zip(distances, points))
    }


def get_elevation_files_pairs() -> list[tuple[Path, Path]]:
    elevations_dir = Path(__file__).parent.parent / "ig5_web" / "data" / "elevations"
    elevation_files = sorted(elevations_dir.glob("*.json"))

    year_files = {}
    for file_ in elevation_files:
        if file_.stem.endswith("_elevation_profile"):
            continue

        year = file_.stem.split("_")[0]
        if year not in year_files:
            year_files[year] = []
        year_files[year].append(file_)

    return [paths for paths in year_files.values()]


def get_routes_elevation_profiles():
    for route_points_path, sampled_points_path in get_elevation_files_pairs():
        data = sort_exact_and_sampled_elevations(route_points_path, sampled_points_path)
        all_points_sorted, all_points_elevations = data

        year = route_points_path.stem
        parent_dir = route_points_path.parent
        elevation_profile_path = parent_dir / f"{year}_elevation_profile.json"
        if elevation_profile_path.exists():
            elevation_profile = make_elevation_profile(all_points_sorted, all_points_elevations)
            with open(elevation_profile_path, "w", encoding="utf-8") as file_handle:
                json.dump(elevation_profile, file_handle, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    get_routes_elevation_data()
    get_routes_elevation_profiles()


# features = []
# line_string_coordinates = []
# for point in all_pts_sorted:
#     lat, lon = point.x, point.y
#     feature = {
#         "type": "Feature",
#         "geometry": {
#             "type": "Point",
#             "coordinates": [lon, lat],
#         },
#         "properties": {
#             "type": "helper",
#             "name": "",
#             "description": "",
#         },
#     }
#     features.append(feature)
#     line_string_coordinates.append([lon, lat])

# line_string_feature = {
#     "type": "Feature",
#     "geometry": {
#         "type": "LineString",
#         "coordinates": line_string_coordinates,
#     },
# }
# features.append(line_string_feature)
# # with open("sorted_points.json", "w", encoding="utf-8") as f:
# #     json.dump({"type": "FeatureCollection", "features": features}, f, ensure_ascii=False, indent=2)
