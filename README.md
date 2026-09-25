# Nearest-Neighbor-GPX

Builds an ordered GPX waypoint file from a list of latitude and longitude pairs.

The program starts at each input waypoint in turn, repeatedly visits the nearest unvisited point, and keeps the shortest of those routes. Distances are calculated as straight-line great-circle distances using the Haversine formula. This is a **greedy approximation** of an open route: it does not return to the start, account for roads or walking paths, or guarantee the globally shortest route.

## Run

Use Python 3.10 or later. From the repository directory:

```sh
python nearest_neighbor.py
```

By default, it reads `waypoints.txt` and writes `testfile.gpx` in the current directory. Running it with these defaults replaces the existing `testfile.gpx`.

Use different paths with:

```sh
python nearest_neighbor.py --input places.txt --output route.gpx
```

The input file has one `latitude,longitude` pair per line:

```text
40.768128,-73.982149
40.768082,-73.981893
40.767840,-73.980967
```

Blank lines are ignored; surrounding spaces are allowed. Latitude must be from −90 to 90 and longitude from −180 to 180. Repeated coordinates are treated as separate waypoints.

The output contains GPX 1.1 `<wpt>` elements in visit order. It is a waypoint list, not a GPX track with road geometry. The script prints the number of visited points and the total straight-line distance in kilometers.
