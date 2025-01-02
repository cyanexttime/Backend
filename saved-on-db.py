import osmnx as ox
from pymongo import MongoClient
from shapely.geometry import mapping  # Import the mapping function

# Connect to MongoDB
client = MongoClient(
    "mongodb+srv://khangvx8803:zg2vEqu9twyEsCyN@potholescanner.grygu.mongodb.net/?retryWrites=true&w=majority&appName=PotholeScanner:3000/"
)
# Connect to MongoDB
# client = MongoClient("mongodb://localhost:27017/")  # Adjust the host and port if needed
db = client["osm_data"]  # Database name

# List of places to download data for
places = [
    "Ho Chi Minh City, Vietnam",
    "Thủ Đức, Ho chi minh city, Vietnam",
    "Dong Hoa, Dĩ An, Vietnam",
]
# Network type (drive, bike, walk, etc.)
network_type = "bike"  # Set the desired network type

for place in places:
    print(f"Downloading data for {place}...")

    # Download a street network for the place
    try:
        G = ox.graph_from_place(place, network_type=network_type)
    except Exception as e:
        print(f"Error downloading data for {place}: {e}")
        continue

    # Convert to GeoDataFrames
    print(f"Converting data to GeoDataFrames for {place}...")
    nodes, edges = ox.graph_to_gdfs(G)

    # Reset index and convert geometries to GeoJSON format
    print(f"Preparing nodes data for {place}...")
    nodes["geometry"] = nodes["geometry"].apply(
        mapping
    )  # Convert Shapely geometries to GeoJSON
    nodes["place"] = place  # Add a field to indicate the place
    nodes_data = nodes.reset_index().to_dict(orient="records")

    print(f"Preparing edges data for {place}...")
    edges["geometry"] = edges["geometry"].apply(
        mapping
    )  # Convert Shapely geometries to GeoJSON
    edges["place"] = place  # Add a field to indicate the place
    edges_data = edges.reset_index().to_dict(orient="records")

    # Save nodes and edges to MongoDB
    print(f"Saving nodes to MongoDB for {place}...")
    db.nodes.insert_many(nodes_data)

    print(f"Saving edges to MongoDB for {place}...")
    db.edges.insert_many(edges_data)

    print(f"Data for {place} saved successfully!")

print("All data saved successfully!")
