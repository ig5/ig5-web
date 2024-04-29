"""
Manually copy coordinates from providet *.doc[x]/*.pdf to a text file. If it's
possible to copy only columns from the source file then put them all in
separate txt files and zip 'em together using Python. Elevation

Expected format is something along lines

    001 N49,23554°  E18,73096° 297 m

or

    N50°31.077' E13°39.344'
"""

from pprint import pprint


def zip_route_lat_lon(lat: str, lon: str) -> tuple:
    lat_lon = []
    for file in (lat, lon):
        with open(file) as f:
            column = []
            for line in f.readlines():
                line = line.strip().replace(" ", "")
                if line:
                    column.append(line)

            lat_lon.append(column)

    return tuple(zip(*lat_lon))


def read_route_lat_lon(lat_lon: str) -> list:
    with open(lat_lon) as f:
        lines = f.readlines()

    lat_lon = []
    for line in lines:
        line = line.strip()
        line = line.split()

        lat_lon.append((line[1], line[2]))

    return lat_lon


def format_coordinate(coordinate: str, indicator: str) -> float:
    coordinate = coordinate.replace(",", ".")
    coordinate = coordinate.replace("'", "")
    coordinate = coordinate.replace(indicator, "")

    parts = coordinate.split("°")
    if len(parts) > 1 and parts[1]:
        degrees = parts[0]
        minutes = parts[1]
        coordinate = float(degrees) + float(minutes) / 60
    else:
        coordinate = coordinate.replace("°", "")
        coordinate = float(coordinate)

    return round(coordinate, 5)


def format_route_points(coordinates: tuple) -> list:
    formatted = []
    for lat, lon in coordinates:
        formatted.append(
            {
                "coordinates": [
                    format_coordinate(lat, "N"),
                    format_coordinate(lon, "E"),
                ],
                "name": "",
                "description": "",
            }
        )
    return formatted


def add_orientational_site_info(route_points):
    counter = 1
    for route_point in route_points:
        if "orientačné" not in route_point["name"]:
            continue

        route_point["name"] = f"{counter}. orientačné stanovisko"
        counter += 1

    return route_points


def main():
    # In case of format `001 N49,23554°  E18,73096° 297 m`.
    # coordinates = read_route_lat_lon("/tmp/lat_lon.txt")

    # In case of format `N50°31.077' E13°39.344'`.
    coordinates = zip_route_lat_lon("/tmp/lat.txt", "/tmp/lon.txt")
    route_points = format_route_points(coordinates)
    route_points = add_orientational_site_info(route_points)
    pprint(route_points)


if __name__ == "__main__":
    main()
