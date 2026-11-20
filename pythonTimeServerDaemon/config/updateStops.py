
import json
import os
from passiogo_fix import passiogo

system = passiogo.getSystemFromID(1007)

stops = system.getStops()

filename = "nyu_stops.json"

# Load existing JSON, or create an empty dictionary
if os.path.exists(filename):
    with open(filename, "r", encoding="utf-8") as file:
        stop_data = json.load(file)
else:
    stop_data = {}

# Add new stops without changing existing values
for stop in stops:
    if stop.name not in stop_data:
        stop_data[stop.name] = False

# Save updated JSON
with open(filename, "w", encoding="utf-8") as file:
    json.dump(stop_data, file, indent=4, ensure_ascii=False)

print(f"Updated {filename}")
print(f"Total stops: {len(stop_data)}")
