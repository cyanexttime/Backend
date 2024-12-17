import requests


def test_shortest_path(server_url, origin, destination):
    url = f"{server_url}/shortest-path"
    payload = {"origin": origin, "destination": destination}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("/shortest-path response:")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error testing /shortest-path: {e}")


def test_render_map(server_url, origin, destination):
    url = f"{server_url}/render-map"
    payload = {"origin": origin, "destination": destination}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("/render-map response:")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error testing /render-map: {e}")


if __name__ == "__main__":
    # Replace with your server URL
    server_url = (
        "http://127.0.0.1:5000"  # Adjust if the server is on a different host/IP
    )

    # Test inputs
    origin = "University of Information Technology, ho chi minh, viet nam"
    destination = "suoi tien, ho chi minh, viet nam"

    print("Testing /shortest-path endpoint...")
    test_shortest_path(server_url, origin, destination)

    print("\nTesting /render-map endpoint...")
    test_render_map(server_url, origin, destination)
