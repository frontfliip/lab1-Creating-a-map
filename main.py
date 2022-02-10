"""
A module for creating a map
"""


import math
import argparse
import folium as fo
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


def parse_info():
    """
    Parsing the arguments
    """
    parser = argparse.ArgumentParser(description='Creaing a map')
    parser.add_argument('-year', type=int, help='needed year')
    parser.add_argument('-latitude', type=float, help='your latitude')
    parser.add_argument('-longitude', type=float, help='your longitude')
    parser.add_argument('-file', type=str, help='The path to a graph file')
    args = parser.parse_args()
    year = args.year
    latitude = args.latitude
    longitude = args.longitude
    file_name = args.file
    return year, latitude, longitude, file_name


def find_distance(lat_1, lat_2, lon_1, lon_2):
    """
    Finding the distance between to coords on Earth
    (float, float, float, float) -> float
    >>> find_distance(12.2344, -23.5637, 16.9087, -44.2746)
    7731.144889848772
    """
    r = 6356
    rad_1 = ((lat_2 - lat_1)/2 * math.pi)/180
    rad_2 = ((lon_2 - lon_1)/2 * math.pi)/180
    sin_1 = math.sin(rad_1) ** 2
    sin_2 = math.sin(rad_2) ** 2
    arg = sin_1 + (math.cos(lat_1 * math.pi / 180) * math.cos(lat_2 * math.pi / 180) * sin_2)
    arg_1 = math.sqrt(arg)
    dist = 2 * r * math.asin(arg_1)
    return dist


def read_file(file_name, year):
    """
    Reading a file and returns a list with needed args
    (str, int) -> list
    """
    with open(file_name, encoding="utf8", errors='ignore') as file:
            lines = file.readlines()
            info = []
            for i in range(len(lines)):
                if i > 13:
                    if str(year) not in lines[i]:
                        continue
                    else:
                        lines[i] = lines[i].replace("\n", "")
                        lines[i] = lines[i].replace("#", "")
                        lines[i] = lines[i].split("\t")
                        times = 0
                        for j in range(len(lines[i])):
                            if len(lines[i][j]) == 0:
                                times += 1
                        for j in range(len(lines[i])):
                            if len(lines[i][j]) == 0:
                                for k in range(times):
                                    lines[i].pop(j)
                                break
                        if "(" in lines[i][-1]:
                            lines[i].pop(-1)
                        if "{" in lines[i][0]:
                            lines[i][0] = lines[i][0].split("{")
                            lines[i][0].pop(1)
                        lines[i][0] = "".join(lines[i][0])
                        lines[i][0] = lines[i][0].split("(")
                        lines[i][0][1] = lines[i][0][1].replace(")", "")
                        lines[i][0][1] = lines[i][0][1].replace(" ", "")
                        lines[i][0][0] = lines[i][0][0][:-1]
                        lines[i][1] = lines[i][1].split(",")
                        if len(lines[i][1]) > 3:
                            extra = len(lines[i][1]) - 3
                            for _ in range(extra):
                                lines[i][1].pop(0)
                        lines[i][1] = "".join(lines[i][1])
                        cur_info = []
                        cur_info.append(lines[i][0][0])
                        cur_info.append(lines[i][0][1])
                        cur_info.append(lines[i][1])
                        info.append(cur_info)
    return info


def get_coords_and_dist(lat, lon, info_locations):
    """
    Gets coordinations of needed places and finds distance
    (float, float, list) -> list
    """
    geolocator = Nominatim(user_agent="main.py")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.001)
    for loc in info_locations:
        try:
            location = geolocator.geocode(loc[2])
            loc.append(location.latitude)
            loc.append(location.longitude)
            distance = find_distance(lat, location.latitude, lon, location.longitude)
            loc.append(distance)
        except:
            info_locations.remove(loc)
            continue
    new_info = []
    for i in range(len(info_locations)):
        if len(info_locations[i]) >= 6:
            new_info.append(info_locations[i])
    return new_info


def get_min(new_info):
    """
    Finds 6 locations with the smallest distance and returns a list
    (list) -> list
    """
    min = 100000000
    closest_locs = []
    while len(closest_locs) != 6:
        min = 100000000
        for i in range(len(new_info)):
            if new_info[i][5] < min:
                min = new_info[i][5]
                current_loc = new_info[i]
        if len(closest_locs) != 0:
            for j in range(len(closest_locs)):
                if closest_locs[j][5] == current_loc[5]:
                    new_info.remove(current_loc)
                    break
                if j == len(closest_locs) - 1:
                    closest_locs.append(current_loc)
                    new_info.remove(current_loc)
        else:
            closest_locs.append(current_loc)
            new_info.remove(current_loc)
    return closest_locs


def get_max(new_info):
    """
    Finds 6 locations with the largest distance and returns a list
    (list) -> list
    """
    maximum = 0
    farthest_locs = []
    while len(farthest_locs) != 6:
        maximum = 0
        for i in range(len(new_info)):
            if new_info[i][5] > maximum:
                maximum = new_info[i][5]
                current_loc = new_info[i]
        if len(farthest_locs) != 0:
            for j in range(len(farthest_locs)):
                if farthest_locs[j][5] == current_loc[5]:
                    new_info.remove(current_loc)
                    break
                if j == len(farthest_locs) - 1:
                    farthest_locs.append(current_loc)
                    new_info.remove(current_loc)
        else:
            farthest_locs.append(current_loc)
            new_info.remove(current_loc)
    return farthest_locs


def create_a_map(farthest_locs, closest_locs, lat, lon):
    """
    Creats a map and saves it
    """

    html_1 = """<h4>{} closest:</h4>
    Location name: {} <br>
    Distance: {} km <br>
    Movie, filmed here: {}
    """
    html_2 = """<h4>{} farthest:</h4>
    Location name: {} <br>
    Distance: {} km <br>
    Movie, filmed here: {}
    """
    map = fo.Map(location=[lat, lon], zoom_start=6)

    fg_list = []
    latitude = []
    longitude = []
    places = []
    distances = []
    movie = []
    for item in closest_locs:
        latitude.append(item[3])
        longitude.append(item[4])
        places.append(item[2])
        item[5] = round(item[5], 0)
        distances.append(item[5])
        movie.append(item[0])
    number_1 = ["The", "Second", "Third", "Fourth", "Fifth", "Sixth"]
    colours_1 = ["darkred", "red", "red", "red", "red", "red"]
    fg = fo.FeatureGroup(name="The closest places, where movies were filmed")
    for lt, ln, pl, ds, mv, num, col in zip(latitude, longitude, places, distances, movie, number_1, colours_1):
        iframe = fo.IFrame(html=html_1.format(num, pl, ds, mv), width=400, height=150)
        fg.add_child(fo.Marker(location=[lt, ln], popup=fo.Popup(iframe), icon=fo.Icon(color=col)))
    fg_list.append(fg)

    latitude = []
    longitude = []
    places = []
    distances = []
    movie = []
    for item in farthest_locs:
        latitude.append(item[3])
        longitude.append(item[4])
        places.append(item[2])
        item[5] = round(item[5], 0)
        distances.append(item[5])
        movie.append(item[0])
    number_2 = ["The", "Second", "Third", "Fourth", "Fifth", "Sixth"]
    colours_2 = ["darkblue", "blue", "blue", "blue", "blue", "blue"]
    fg = fo.FeatureGroup(name="The farthest places, where movies were filmed")
    for lt, ln, pl, ds, mv, num, col in zip(latitude, longitude, places, distances, movie, number_2, colours_2):
        iframe = fo.IFrame(html=html_2.format(num, pl, ds, mv), width=400, height=150)
        fg.add_child(fo.Marker(location=[lt, ln], popup=fo.Popup(iframe), icon=fo.Icon(color=col, )))
    fg_list.append(fg)

    for fg in fg_list:
        map.add_child(fg)
    map.add_child(fo.LayerControl())
    map.save('New_map.html')


def main():
    """
    main func
    """
    year, lat, lon, file_name,  = parse_info()
    info = read_file(file_name, year)
    info_with_coords = get_coords_and_dist(lat, lon, info)
    closest_locs = get_min(info_with_coords)
    farthest_locs = get_max(info_with_coords)
    create_a_map(farthest_locs, closest_locs, lat, lon)


if __name__ == "__main__":
    main()
