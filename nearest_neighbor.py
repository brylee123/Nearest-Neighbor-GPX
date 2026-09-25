"""Build a nearest-neighbor GPX route from a list of latitude,longitude pairs.

This is an open route: it visits every waypoint without returning to its start.
Trying every start improves the greedy result, but does not guarantee the
globally shortest route.
"""

from __future__ import annotations

import argparse
import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

EARTH_RADIUS_KM = 6371.0
GPX_NAMESPACE = "http://www.topografix.com/GPX/1/1"


@dataclass(frozen=True)
class Waypoint:
    latitude: float
    longitude: float
    latitude_text: str
    longitude_text: str

    def __str__(self) -> str:
        """Retain the coordinate spelling from the input file."""
        return f"{self.latitude_text},{self.longitude_text}"


def parse_waypoint(line: str, line_number: int) -> Waypoint:
    """Read and validate one latitude,longitude line."""
    parts = line.split(",")
    if len(parts) != 2:
        raise ValueError(f"Line {line_number}: expected latitude,longitude")

    latitude_text, longitude_text = (part.strip() for part in parts)
    try:
        latitude = float(latitude_text)
        longitude = float(longitude_text)
    except ValueError as exc:
        raise ValueError(f"Line {line_number}: coordinates must be numbers") from exc

    if not math.isfinite(latitude) or not -90 <= latitude <= 90:
        raise ValueError(f"Line {line_number}: latitude must be between -90 and 90")
    if not math.isfinite(longitude) or not -180 <= longitude <= 180:
        raise ValueError(f"Line {line_number}: longitude must be between -180 and 180")

    return Waypoint(latitude, longitude, latitude_text, longitude_text)


def read_waypoints(path: Path) -> list[Waypoint]:
    """Load coordinates, ignoring empty lines."""
    with path.open(encoding="utf-8") as source:
        waypoints = [
            parse_waypoint(line.strip(), number)
            for number, line in enumerate(source, start=1)
            if line.strip()
        ]
    if not waypoints:
        raise ValueError(f"{path} contains no waypoints")
    return waypoints


def distance_km(first: Waypoint, second: Waypoint) -> float:
    """Calculate great-circle distance using the Haversine formula."""
    latitude_1 = math.radians(first.latitude)
    latitude_2 = math.radians(second.latitude)
    latitude_change = latitude_2 - latitude_1
    longitude_change = math.radians(second.longitude - first.longitude)

    haversine = (
        math.sin(latitude_change / 2) ** 2
        + math.cos(latitude_1)
        * math.cos(latitude_2)
        * math.sin(longitude_change / 2) ** 2
    )
    # Clamp tiny floating-point overshoots at antipodal coordinates.
    arc = 2 * math.atan2(
        math.sqrt(min(1.0, haversine)),
        math.sqrt(max(0.0, 1.0 - haversine)),
    )
    return EARTH_RADIUS_KM * arc


def distance_table(waypoints: Sequence[Waypoint]) -> list[list[float]]:
    """Calculate each pair once; all starting points reuse the same distances."""
    size = len(waypoints)
    distances = [[0.0] * size for _ in range(size)]
    for first in range(size):
        for second in range(first + 1, size):
            distance = distance_km(waypoints[first], waypoints[second])
            distances[first][second] = distance
            distances[second][first] = distance
    return distances


def nearest_neighbor_route(
    start: int, distances: Sequence[Sequence[float]], distance_limit: float = math.inf
) -> tuple[list[int], float]:
    """Greedily visit the nearest unvisited point from one starting index."""
    size = len(distances)
    visited = bytearray(size)
    visited[start] = 1
    route = [start]
    total_km = 0.0

    while len(route) < size:
        current = route[-1]
        closest = -1
        shortest_leg = math.inf
        for candidate in range(size):
            # Strict comparison preserves input order when two distances tie.
            if not visited[candidate] and distances[current][candidate] < shortest_leg:
                closest = candidate
                shortest_leg = distances[current][candidate]

        total_km += shortest_leg
        if total_km >= distance_limit:
            return route, total_km  # This start cannot improve the best full route.
        visited[closest] = 1
        route.append(closest)

    return route, total_km


def best_route(waypoints: Sequence[Waypoint]) -> tuple[list[Waypoint], float]:
    """Try every starting point and keep the shortest greedy open route."""
    distances = distance_table(waypoints)
    best_indices: list[int] = []
    best_length = math.inf

    for start in range(len(waypoints)):
        indices, length = nearest_neighbor_route(start, distances, best_length)
        if len(indices) == len(waypoints) and length < best_length:
            best_indices, best_length = indices, length

    return [waypoints[index] for index in best_indices], best_length


def write_gpx(path: Path, route: Sequence[Waypoint]) -> None:
    """Write the ordered route as GPX 1.1 waypoints."""
    ET.register_namespace("", GPX_NAMESPACE)
    gpx = ET.Element(f"{{{GPX_NAMESPACE}}}gpx", version="1.1", creator="Nearest-Neighbor-GPX")
    for point in route:
        ET.SubElement(
            gpx,
            f"{{{GPX_NAMESPACE}}}wpt",
            lat=point.latitude_text,
            lon=point.longitude_text,
        )
    ET.ElementTree(gpx).write(path, encoding="utf-8", xml_declaration=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=Path("waypoints.txt"),
        help="coordinate file (default: waypoints.txt)",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("testfile.gpx"),
        help="GPX destination (default: testfile.gpx)",
    )
    args = parser.parse_args(argv)

    try:
        waypoints = read_waypoints(args.input)
        route, length = best_route(waypoints)
        write_gpx(args.output, route)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print(f"Visited {len(route)} waypoints across {length:.3f} km.")
    print(f"GPX route written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
