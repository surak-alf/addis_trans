import pandas as pd
import simplekml
from pathlib import Path

BASE = Path("../data/filtered_gtfs")
OUT = Path("../outputs/filtered_routes.kml")

print("Loading filtered GTFS...")

routes = pd.read_csv(BASE / "routes.txt")
trips = pd.read_csv(BASE / "trips.txt")
stops = pd.read_csv(BASE / "stops.txt")

shapes = None
if (BASE / "shapes.txt").exists():
    shapes = pd.read_csv(BASE / "shapes.txt")

kml = simplekml.Kml()

# -----------------------------------------
# Build route_id → color map
# -----------------------------------------
COLOR_LIST = [
    simplekml.Color.red,
    simplekml.Color.blue,
    simplekml.Color.green,
    simplekml.Color.orange,
    simplekml.Color.purple,
    simplekml.Color.cyan,
]

route_ids = routes["route_id"].unique()
route_color = {
    rid: COLOR_LIST[i % len(COLOR_LIST)]
    for i, rid in enumerate(route_ids)
}

# -----------------------------------------
# Draw ROUTE SHAPES grouped by route
# -----------------------------------------
if shapes is not None and "shape_id" in trips.columns:

    print("Building colored route lines...")

    for route_id in route_ids:

        route_name = routes[routes["route_id"] == route_id].iloc[0]["route_short_name"]
        color = route_color[route_id]

        folder = kml.newfolder(name=f"Route {route_name}")

        route_trips = trips[trips["route_id"] == route_id]

        for shape_id in route_trips["shape_id"].dropna().unique():

            group = shapes[shapes["shape_id"] == shape_id] \
                        .sort_values("shape_pt_sequence")

            coords = list(zip(group.shape_pt_lon, group.shape_pt_lat))

            if len(coords) < 2:
                continue

            line = folder.newlinestring(
                name=f"{route_name} shape {shape_id}",
                coords=coords
            )

            line.style.linestyle.width = 5
            line.style.linestyle.color = color

print("Shapes added")

# -----------------------------------------
# Add STOPS (single folder)
# -----------------------------------------
print("Adding stops...")

stop_folder = kml.newfolder(name="Stops")

for _, stop in stops.iterrows():
    pnt = stop_folder.newpoint(
        name=str(stop["stop_name"]),
        coords=[(stop["stop_lon"], stop["stop_lat"])]
    )
    pnt.style.iconstyle.scale = 0.8

print("Stops added")

# -----------------------------------------
# Save
# -----------------------------------------
kml.save(str(OUT))

print("✅ Colored KML created at:", OUT)
