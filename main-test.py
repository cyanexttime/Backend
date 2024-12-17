import webbrowser
import osmnx as ox
import networkx as nx
from pymongo import MongoClient
from shapely.geometry import shape
import folium

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Adjust the host and port if needed
db = client["osm_data_1"]  # Database name
nodes_collection = db.nodes
edges_collection = db.edges


def reconstruct_graph(nodes, edges):
    """Reconstruct the graph from nodes and edges, and save to a file."""
    G = nx.MultiDiGraph()
    G.graph["crs"] = "EPSG:4326"  # WGS84

    # Add nodes
    for node in nodes:
        geometry = shape(node.pop("geometry"))
        G.add_node(node["osmid"], **node, geometry=geometry)

    # Add edges
    for edge in edges:
        geometry = shape(edge.pop("geometry"))
        G.add_edge(edge["u"], edge["v"], **edge, geometry=geometry)

    print("Graph reconstructed successfully!")
    return G


def find_shortest_path(G, origin_coords, destination_coords):
    """Find the shortest path between two coordinates using Dijkstra's algorithm."""
    # Find nearest nodes to origin and destination
    origin_node = ox.distance.nearest_nodes(G, X=origin_coords[1], Y=origin_coords[0])
    destination_node = ox.distance.nearest_nodes(
        G, X=destination_coords[1], Y=destination_coords[0]
    )

    print(f"Origin Node: {origin_node}, Destination Node: {destination_node}")

    # Calculate shortest path using Dijkstra's algorithm
    path = nx.shortest_path(
        G, source=origin_node, target=destination_node, weight="length"
    )
    return path


# Fetch the nodes and edges from MongoDB
nodes = list(nodes_collection.find())  # List of nodes
edges = list(edges_collection.find())  # List of edges

# Reconstruct the graph
G = reconstruct_graph(nodes, edges)

# Define the origin and destination places
origin_place = "University of Information Technology, Ho Chi Minh, Vietnam"
destination_place = "Notre-Dame Cathedral Basilica of Saigon, Ho Chi Minh, Vietnam"

# Geocode places to get coordinates
origin_coords = ox.geocode(origin_place)
destination_coords = ox.geocode(destination_place)

print(f"Origin Coordinates: {origin_coords}")
print(f"Destination Coordinates: {destination_coords}")

# Find the shortest path
path = find_shortest_path(G, origin_coords, destination_coords)

# Print all nodes in the path
print("Nodes in the shortest path:")
for node in path:
    print(
        f"Node ID: {node}, Coordinates: ({G.nodes[node]['geometry'].y}, {G.nodes[node]['geometry'].x})"
    )

# Create a folium map
map_path = folium.Map(location=origin_coords, zoom_start=14, tiles="OpenStreetMap")

# Add the shortest path to the map
path_coords = [
    (G.nodes[node]["geometry"].y, G.nodes[node]["geometry"].x) for node in path
]
folium.PolyLine(path_coords, color="blue", weight=5, opacity=0.8).add_to(map_path)
