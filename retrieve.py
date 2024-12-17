from pymongo import MongoClient
import networkx as nx
from shapely.geometry import shape

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["osm_data"]

# Load nodes and edges from MongoDB
nodes = list(db.nodes.find())
edges = list(db.edges.find())

# Create a graph object
G = nx.MultiDiGraph()

# Add nodes to the graph
for node in nodes:
    G.add_node(node["osmid"], **node, geometry=shape(node["geometry"]))

# Add edges to the graph
for edge in edges:
    G.add_edge(edge["u"], edge["v"], **edge, geometry=shape(edge["geometry"]))

print("Graph reconstructed successfully!")
