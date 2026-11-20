import requests

API_KEY = ""
BASE_URL = "https://api.tomtom.com/routing/1/calculateRoute"


def drive_time_minutes(origin, destination, depart_at=None):
    """Estimate car travel time between two (lat, lon) pairs.

    origin, destination: (latitude, longitude) tuples
    depart_at: optional ISO 8601 string, e.g. "2026-11-19T17:00:00-05:00"
    Returns the estimated travel time in minutes (traffic-aware).
    """
    locations = f"{origin[0]},{origin[1]}:{destination[0]},{destination[1]}"
    params = {
        "key": API_KEY,
        "traffic": "true",
        "travelMode": "car",
        "routeRepresentation": "summaryOnly",
    }
    if depart_at:
        params["departAt"] = depart_at

    response = requests.get(f"{BASE_URL}/{locations}/json", params=params, timeout=10)
    response.raise_for_status()

    summary = response.json()["routes"][0]["summary"]
    return summary["travelTimeInSeconds"] / 60


def drive_time_minutes_along_path(points, depart_at=None):
    """Estimate driving time while following ordered (lat, lon) route points."""
    if len(points) < 2:
        raise ValueError("path needs at least 2 points")

    origin, destination = points[0], points[-1]
    locations = f"{origin[0]},{origin[1]}:{destination[0]},{destination[1]}"
    params = {
        "key": API_KEY,
        "traffic": "true",
        "travelMode": "car",
        "routeType": "shortest",
        "routeRepresentation": "summaryOnly",
        "computeTravelTimeFor": "all",
    }
    if depart_at:
        params["departAt"] = depart_at

    response = requests.post(
        f"{BASE_URL}/{locations}/json",
        params=params,
        json={
            "supportingPoints": [
                {"latitude": point[0], "longitude": point[1]}
                for point in points
            ]
        },
        timeout=10,
    )
    response.raise_for_status()

    summary = response.json()["routes"][0]["summary"]
    return summary["noTrafficTravelTimeInSeconds"] / 60



#TEST IF RUN DIRECTLY
if __name__ == "__main__":
    times_square = (40.7580, -73.9855)
    jfk = (40.6413, -73.7781)

    minutes = drive_time_minutes(times_square, jfk)
    print(f"Estimated drive time: {minutes:.0f} minutes")
