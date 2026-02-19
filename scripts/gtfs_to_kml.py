import pandas as pd
import simplekml
from pathlib import Path

BASE = Path("../data/filtered_gtfs")
OUT = Path("../outputs/filtered_routes.kml")

print("Loading filtered GTFS...")

routes = pd.read_csv(BASE / "routes.txt")
trips = pd.read_csv(BASE / "trips.txt")

shapes = None
if (BASE / "shapes.txt").exists():
    shapes = pd.read_csv(BASE / "shapes.txt")

stops = pd.read_csv(BASE / "stops.txt")

kml = simplekml.Kml()

# -------------------------------------------------
# Draw ROUTE SHAPES (polylines)
# -------------------------------------------------
if shapes is not None and "shape_id" in trips.columns:

    print("Building shape lines...")

    for shape_id, group in shapes.groupby("shape_id"):
        group = group.sort_values("shape_pt_sequence")

        coords = list(zip(group.shape_pt_lon, group.shape_pt_lat))

        # find route name from trips → routes
        trip_row = trips[trips["shape_id"] == shape_id].iloc[0]
        route_id = trip_row["route_id"]
        route_name = routes[routes["route_id"] == route_id].iloc[0]["route_short_name"]

        line = kml.newlinestring(
            name=f"Route {route_name}",
            coords=coords
        )

        line.style.linestyle.width = 4

print("Shapes added")

# -------------------------------------------------
# Add STOPS (points)
# -------------------------------------------------
print("Adding stops...")

for _, stop in stops.iterrows():
    pnt = kml.newpoint(
        name=str(stop["stop_name"]),
        coords=[(stop["stop_lon"], stop["stop_lat"])]
    )
    pnt.style.iconstyle.scale = 0.8

print("Stops added")

# -------------------------------------------------
# Save KML
# -------------------------------------------------
kml.save(str(OUT))

print("✅ KML created at:", OUT)
