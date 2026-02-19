import pandas as pd
from pathlib import Path

RAW = Path("../data/raw_gtfs")
OUT = Path("../data/filtered_gtfs")

OUT.mkdir(parents=True, exist_ok=True)

# -----------------------------
# TARGET ROUTES (edit if needed)
# -----------------------------
TARGET_ROUTE_SHORT_NAMES = [
    "AB097",
    "AB049"
]

print("Loading GTFS files...")

routes = pd.read_csv(RAW / "routes.txt")
trips = pd.read_csv(RAW / "trips.txt")
stop_times = pd.read_csv(RAW / "stop_times.txt")
stops = pd.read_csv(RAW / "stops.txt")

shapes = None
if (RAW / "shapes.txt").exists():
    shapes = pd.read_csv(RAW / "shapes.txt")

calendar = None
if (RAW / "calendar.txt").exists():
    calendar = pd.read_csv(RAW / "calendar.txt")

# --------------------------------------------------
# 1️⃣ Filter routes
# --------------------------------------------------
routes_f = routes[routes["route_short_name"].isin(TARGET_ROUTE_SHORT_NAMES)]
route_ids = set(routes_f["route_id"])

print("Selected routes:", route_ids)

# --------------------------------------------------
# 2️⃣ Filter trips
# --------------------------------------------------
trips_f = trips[trips["route_id"].isin(route_ids)]
trip_ids = set(trips_f["trip_id"])

print("Trips kept:", len(trip_ids))

# --------------------------------------------------
# 3️⃣ Filter stop_times
# --------------------------------------------------
stop_times_f = stop_times[stop_times["trip_id"].isin(trip_ids)]
stop_ids = set(stop_times_f["stop_id"])

print("Stops used:", len(stop_ids))

# --------------------------------------------------
# 4️⃣ Filter stops
# --------------------------------------------------
stops_f = stops[stops["stop_id"].isin(stop_ids)]

# --------------------------------------------------
# 5️⃣ Filter shapes (if exists)
# --------------------------------------------------
if shapes is not None and "shape_id" in trips_f.columns:
    shape_ids = set(trips_f["shape_id"].dropna())
    shapes_f = shapes[shapes["shape_id"].isin(shape_ids)]
else:
    shapes_f = None

# --------------------------------------------------
# 6️⃣ Filter calendar (if exists)
# --------------------------------------------------
if calendar is not None:
    service_ids = set(trips_f["service_id"])
    calendar_f = calendar[calendar["service_id"].isin(service_ids)]
else:
    calendar_f = None

# --------------------------------------------------
# SAVE FILES
# --------------------------------------------------
print("Saving filtered GTFS...")

routes_f.to_csv(OUT / "routes.txt", index=False)
trips_f.to_csv(OUT / "trips.txt", index=False)
stop_times_f.to_csv(OUT / "stop_times.txt", index=False)
stops_f.to_csv(OUT / "stops.txt", index=False)

if shapes_f is not None:
    shapes_f.to_csv(OUT / "shapes.txt", index=False)

if calendar_f is not None:
    calendar_f.to_csv(OUT / "calendar.txt", index=False)

print("✅ Filtering complete!")
