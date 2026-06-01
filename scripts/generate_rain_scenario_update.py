import os
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import random

# ==============================================================
# PROJECT STRUCTURE
# ==============================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
BASELINE_SCENARIO = os.path.join(PROJECT_ROOT, "scenarios", "baseline")
RAIN_SCENARIO = os.path.join(PROJECT_ROOT, "scenarios", "rain")
HISTORICAL_RAIN_DATA = r"C:\Users\USER\OneDrive\Desktop\ICT\Major project\project simulations\data\weather\historical_rain_data.csv"

# ==============================================================
# CONFIGURATION
# ==============================================================
RAIN_INTENSITY = {
    "none": {"ped_duration_range": (25, 35), "veh_speed": 13.89},
    "light": {"ped_duration_range": (40, 55), "veh_speed": 10.0},
    "moderate": {"ped_duration_range": (55, 70), "veh_speed": 8.0},
    "heavy": {"ped_duration_range": (80, 100), "veh_speed": 5.0}
}

def get_rain_intensity(rainfall):
    if rainfall < 0.1:
        return "none"
    elif 0.1 <= rainfall < 5.0:
        return "light"
    elif 5.0 <= rainfall < 15.0:
        return "moderate"
    else:
        return "heavy"

def generate_rain_scenario_routes():
    # Check file paths
    if not os.path.exists(HISTORICAL_RAIN_DATA):
        raise FileNotFoundError(f"Rain data file not found at: {HISTORICAL_RAIN_DATA}")
    if not os.path.exists(BASELINE_SCENARIO):
        raise FileNotFoundError(f"Baseline scenario folder not found at: {BASELINE_SCENARIO}")
    os.makedirs(RAIN_SCENARIO, exist_ok=True)

    # Read rainfall data
    max_rainfall = 0.0
    with open(HISTORICAL_RAIN_DATA, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rainfall = float(row["Rainfall (mm/h)"])
                if rainfall > max_rainfall:
                    max_rainfall = rainfall
            except (ValueError, KeyError):
                continue

    # Get rain intensity and effects
    intensity = get_rain_intensity(max_rainfall)
    effects = RAIN_INTENSITY[intensity]
    ped_min, ped_max = effects["ped_duration_range"]
    veh_speed = effects["veh_speed"]

    print(f"[INFO] Max rainfall observed: {max_rainfall} mm/h")
    print(f"[INFO] Rain intensity: {intensity.upper()}")
    print(f"[INFO] Pedestrian walk duration: {ped_min}-{ped_max} sec")
    print(f"[INFO] Vehicle max speed: {veh_speed} m/s")

    # ========== MODIFY VEHICLES ==========
    veh_in = os.path.join(BASELINE_SCENARIO, "vehicles.rou.xml")
    veh_out = os.path.join(RAIN_SCENARIO, "vehicles.rou.xml")
    veh_tree = ET.parse(veh_in)
    for vType in veh_tree.findall(".//vType"):
        vType.set("maxSpeed", str(veh_speed))
    veh_tree.write(veh_out)

    # ========== MODIFY PEDESTRIANS ==========
    ped_in = os.path.join(BASELINE_SCENARIO, "pedestrians.rou.xml")
    ped_out = os.path.join(RAIN_SCENARIO, "pedestrians.rou.xml")
    ped_tree = ET.parse(ped_in)

    for person in ped_tree.findall(".//person"):

        # Randomize walk duration within range
        walk_elem = person.find("walk")
        if walk_elem is not None:
            duration = random.randint(ped_min, ped_max)
            walk_elem.set("duration", str(duration))

    ped_tree.write(ped_out)

    print(f"[SUCCESS] Rain scenario files written to: {RAIN_SCENARIO}")

if __name__ == "__main__":
    generate_rain_scenario_routes()
