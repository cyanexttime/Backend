import osmnx as ox
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI
db = client["map_data"]  # Database name
nodes_collection = db["nodes"]  # Collection for nodes
edges_collection = db["edges"]  # Collection for edges
places_collection = db["places"]  # Collection for place names

# Define the place to download
place_name = "Ho Chi Minh city, Viet Nam"

# Download the graph
graph = ox.graph_from_place(place_name, network_type="all")

# Extract nodes and edges as DataFrames
nodes, edges = ox.graph_to_gdfs(graph, nodes=True, edges=True)

# Convert GeoDataFrames to dictionaries for MongoDB
nodes_dict = nodes.to_dict(orient="records")
edges_dict = edges.to_dict(orient="records")

north, south, east, west = ox.utils_geo.bbox_from_gdf(nodes)
nodes_coordinates = nodes[["x", "y"]].to_dict(orient="records")

# Save nodes and edges to MongoDB
nodes_collection.insert_many(nodes_dict)
edges_collection.insert_many(edges_dict)

# Save place metadata
places_collection.insert_one(
    {
        "place_name": place_name,
        "nodes_count": len(nodes),
        "edges_count": len(edges),
        "bounding_box": {"north": north, "south": south, "east": east, "west": west},
        "nodes_coordinates": nodes_coordinates,  # Optional, but can be large for large areas
    }
)

print(f"Data for {place_name} saved successfully!")
