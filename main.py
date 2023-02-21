'''Module that creates map with films'''
import folium
import argparse
from haversine import haversine
from geopy.geocoders import Nominatim

parser = argparse.ArgumentParser(description='A program that creates map with labels on it')
parser.add_argument('year', type=str, help="This is a year of the film that will be searched")
parser.add_argument('latitude', type=str, help="This is a latitude of a starting point")
parser.add_argument('longtitude', type=str, help="This is a longtitude of a starting point")
parser.add_argument('path', type=str, help="This is file with the movies")

args = parser.parse_args()

year = args.year
latitude = args.latitude
longtitude = args.longtitude
path = args.path

def read_file(path: str, year: str) -> list:
    '''
    The function reads given file and returns list of lists,
    every list contains movie name, year of the movie and location
    >>> len(read_file('loc.txt', 2009))
    20
    '''
    file_list = []
    geolocator = Nominatim(user_agent="my_name")
    with open(path, 'r', encoding = 'utf-8') as file:
        for row in file:
            if str(year) in row:
                if '\t' in row:
                      row = row.replace('\t', '')
                if '"' in row[2:] and '{' in row :
                    second_duzka = row.index('}')
                    first_oval = row.index('(')
                    second_oval = row.index(')')
                    row =row[:first_oval]+ ';' + row[first_oval:second_oval+2] +';' + row[second_duzka + 1:]
                    row = row.strip('\n')
                    row = row.split(';')
                    file_list.append(row)
                elif '(' in row: 
                    first_oval = row.index('(')
                    second_oval = row.index(')')
                    row = row[:first_oval]+ ';' + row[first_oval:second_oval+1] +';' + row[second_oval + 1:]
                    row = row.strip('\n')
                    row = row.split(';')
                    file_list.append(row)
    counter = 0
    while counter < len(file_list):
        for row in file_list:
            try:
                location = geolocator.geocode(row[-1])
                row.append([location.latitude, location.longitude])
                counter += 1
            except AttributeError:
                counter+=1
                continue
    vuvid = []
    for item in file_list:
        if len(item) == 4:
            vuvid.append(item)  
    return vuvid

def distance(filelist: list, latitude: float, longtitude: float) -> list:
    '''
    this function calculate the distanse beetwen starting point(latitude; langtitude)
    and (latitude; langtitude) of the movies and return the list
    with 10 movies that have the nearest location to the starting point
    >>> distance(read_file('loc.txt', 2009), 49.83826, 24.02324)[0]
    ['"1-2-3 Istanbul!" ', '(2009)', 'Zagreb, Croatia', [45.84264135, 15.962231476593626], 747.2190046722789]
    '''
    starting_point = (latitude, longtitude)
    for row in filelist:
        dist = haversine(starting_point, row[-1])
        row.append(dist)
    filelist = sorted(filelist, key = lambda x :x[-1])
    if len(filelist) >=10:
        return filelist[:10]
    else:
        return filelist


def map_add(filelist: list, latitude: float, longtitude: float) -> None:
    '''
    This is a main function that creates a map,
    at first it check whether there are any locations with the same latitude and longtitude,
    if yes - > the function adds 0.00000025 to them, in order to make all map.childs visible
    >>> map_add(distance(read_file('loc.txt', 2009), 49.83826, 24.02324),  49.83826, 24.02324)

    '''
    alpha = 0.00000025
    beta = 0.00000025
    for row in filelist:
        if filelist.count(row[-2]) != 1:
            row[-2][0] += alpha
            row[-2][1] += beta
            alpha += 0.00000025
            beta += 0.00000025
    map = folium.Map(tiles= 'openstreetmap',
                        location=[latitude, longtitude],
                        zoom_start=5)
    html = """<h4>Movie information:</h4>
    Movie name: {},<br>
    Year: {}
    """
    
    map.add_child(folium.Marker(location=[latitude, longtitude],
                                    icon=folium.Icon(color = "blue")))
    
    for i in (filelist):
            iframe = folium.IFrame(html=html.format(i[0], i[1]),
                          width=300,
                          height=100)
            map.add_child(folium.Marker(location=[i[-2][0], i[-2][1]],
                                    popup=folium.Popup(iframe),
                                    icon=folium.Icon(color = "red")))
    folium.LayerControl().add_to(map)
    map.save('Maps_Maker.html')


if __name__=="__main__":
    map_add(distance(read_file(path, year), float(latitude), float(longtitude)), float(latitude), float(longtitude))
#     import doctest
#     print(doctest.testmod()) 
