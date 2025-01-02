from flask import Flask, request, jsonify
import osmnx as ox
import networkx as nx
from pymongo import MongoClient
from shapely.geometry import shape
import folium
import os

app = Flask(__name__)

# # Connect to MongoDB
client = MongoClient(
    "mongodb+srv://khangvx8803:zg2vEqu9twyEsCyN@potholescanner.grygu.mongodb.net/?retryWrites=true&w=majority&appName=PotholeScanner:3000/"
)  # Adjust the host and port if needed
# client = MongoClient("mongodb://localhost:27017/")
db = client["osm_data"]  # Database name
nodes_collection = db.nodes
edges_collection = db.edges

# Reconstruct graph
nodes = list(nodes_collection.find())
edges = list(edges_collection.find())
G = nx.MultiDiGraph()
G.graph["crs"] = "EPSG:4326"  # WGS84
for node in nodes:
    geometry = shape(node.pop("geometry"))
    G.add_node(node["osmid"], **node, geometry=geometry)
for edge in edges:
    geometry = shape(edge.pop("geometry"))
    G.add_edge(edge["u"], edge["v"], **edge, geometry=geometry)


@app.route("/shortest-path", methods=["POST"])
def shortest_path():
    data = request.json
    origin_place = data.get("origin")
    destination_place = data.get("destination")

    # Geocode origin and destination
    origin_coords = ox.geocode(origin_place)
    destination_coords = ox.geocode(destination_place)

    # Find nearest nodes
    origin_node = ox.distance.nearest_nodes(G, X=origin_coords[1], Y=origin_coords[0])
    destination_node = ox.distance.nearest_nodes(
        G, X=destination_coords[1], Y=destination_coords[0]
    )

    # Compute shortest path
    path = nx.shortest_path(
        G, source=origin_node, target=destination_node, weight="length"
    )

    # Extract path coordinates
    path_coords = [
        {"lat": G.nodes[node]["geometry"].y, "lon": G.nodes[node]["geometry"].x}
        for node in path
    ]
    return jsonify({"path": path_coords})


@app.route("/render-map", methods=["POST"])
def render_map():
    data = request.json
    origin_place = data.get("origin")
    destination_place = data.get("destination")

    # Geocode origin and destination
    origin_coords = ox.geocode(origin_place)
    destination_coords = ox.geocode(destination_place)

    # Find nearest nodes
    origin_node = ox.distance.nearest_nodes(G, X=origin_coords[1], Y=origin_coords[0])
    destination_node = ox.distance.nearest_nodes(
        G, X=destination_coords[1], Y=destination_coords[0]
    )

    # Compute shortest path
    path = nx.shortest_path(
        G, source=origin_node, target=destination_node, weight="length"
    )

    # Create map with folium
    m = folium.Map(location=[origin_coords[0], origin_coords[1]], zoom_start=14)
    folium.Marker(origin_coords, tooltip="Origin").add_to(m)
    folium.Marker(destination_coords, tooltip="Destination").add_to(m)

    # Add path to map
    path_coords = [
        (G.nodes[node]["geometry"].y, G.nodes[node]["geometry"].x) for node in path
    ]
    folium.PolyLine(path_coords, color="blue", weight=5).add_to(m)

    # Save map to an HTML file
    map_path = "map.html"
    m.save(map_path)

    path_coords = []
    for node in path:
        node_geom = G.nodes[node]["geometry"]
        path_coords.append({"lat": node_geom.y, "lon": node_geom.x})

    # Return the path as a JSON response
    return jsonify({"path": path_coords})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
