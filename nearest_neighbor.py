import math

waypoints = []
with open('waypoints.txt') as inputfile:
	for line in inputfile:
		waypoints.append(line.strip())


def d_between(lat1,lon1,lat2,lon2):
	R = 6371e3

	phi1 = math.radians(lat1)
	phi2 = math.radians(lat2)
	delta_phi = math.radians(lat2-lat1)
	delta_lambda = math.radians(lon2-lon1)

	a = math.sin(delta_phi/2) * math.sin(delta_phi/2) + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2) * math.sin(delta_lambda/2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	
	return R*c/1000 # Distance in kilometers

def adjacent_parse(root, route, length, visited):
	shortest = 9223372036854775807 # Max Int
	closest = ""
	visited.add(root)

	lat1,lon1 = root.split(",")
	lat1,lon1 = float(lat1), float(lon1)

	for neighbor in waypoints:

		if len(route) == len(waypoints):
			return route, length

		if neighbor == root or neighbor in visited: # Skip self and visited nodes
			continue

		lat2,lon2 = neighbor.split(",")
		lat2,lon2 = float(lat2), float(lon2)

		distance = d_between(lat1,lon1,lat2,lon2)

		if distance < shortest:
			#print("\tnew shortest is", distance)
			shortest = distance
			closest = neighbor

	# After we determined the closest node:
	length += shortest
	#print(len(visited), "total length is", length)
	route.append(closest)

	if len(route) != len(waypoints):
		return adjacent_parse(closest, route, length, visited)
	else:
		return route, length

routes = []
route_lengths = []
for i in range(len(waypoints)):
	
	lat1,lon1 = waypoints[i].split(",")
	lat1,lon1 = float(lat1), float(lon1)
	
	start_point = waypoints[i]
	route, route_length = adjacent_parse(start_point, [start_point], 0, set())
	
	routes.append(route)
	route_lengths.append(route_length)

print(route_lengths)

shortest_length = min(route_lengths)
shortest_route = routes[route_lengths.index(shortest_length)] # Indicies are tied together

print("Shortest Route:\n", shortest_route)
print("Shortest Length:\n", shortest_length)

# GPX Output
file = open("testfile.gpx","w")

header = "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"yes\"?>\n<gpx version=\"1.1\" creator=\"GPS Visualizer http://www.gpsvisualizer.com/\" xmlns=\"http://www.topografix.com/GPX/1/1\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd\">\n"
content_head = "<wpt lat=\""
content_seperator = "\" lon=\""
content_tail = "\"></wpt>\n"
footer = "</gpx>"

file.write(header)
for coord in shortest_route:
	data = coord.replace(",", content_seperator)
	content = content_head + data + content_tail
	file.write(content)
file.write(footer)
