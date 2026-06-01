import os
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import random

# ========= CONFIGURABLE PROJECT STRUCTURE ========= #
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
BASELINE_SCENARIO = os.path.join(PROJECT_ROOT, "scenarios", "baseline")
RAIN_SCENARIO = os.path.join(PROJECT_ROOT, "scenarios", "rain adaptive")
HISTORICAL_RAIN_DATA = os.path.join(DATA_DIR, "weather", "historical_rain_data.csv")

# ========= RAIN INTENSITY RULES ========= #
RAIN_INTENSITY = {
    "none": {"ped_duration": 30, "veh_speed": 13.89},
    "light": {"ped_duration": 45, "veh_speed": 11.5},
    "moderate": {"ped_duration": 60, "veh_speed": 9.0},
    "heavy": {"ped_duration": 90, "veh_speed": 7.0}
}

def get_rain_intensity(rainfall):
    """Classify rain intensity based on mm/h values"""
    if rainfall < 0.1:
        return "none"
    elif rainfall < 5.0:
        return "light"
    elif rainfall < 15.0:
        return "moderate"
    else:
        return "heavy"

def generate_rain_adaptive_scenario():
    # ==== Check project structure ====
    if not os.path.exists(HISTORICAL_RAIN_DATA):
        raise FileNotFoundError(f"Missing rainfall data file: {HISTORICAL_RAIN_DATA}")
    if not os.path.exists(BASELINE_SCENARIO):
        raise FileNotFoundError(f"Missing baseline scenario: {BASELINE_SCENARIO}")
    os.makedirs(RAIN_SCENARIO, exist_ok=True)

    # ==== Read worst-case rainfall value ====
    max_rainfall = 0.0
    with open(HISTORICAL_RAIN_DATA, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rainfall = float(row["Rainfall (mm/h)"])
            if rainfall > max_rainfall:
                max_rainfall = rainfall

    rain_type = get_rain_intensity(max_rainfall)
    ped_time = RAIN_INTENSITY[rain_type]["ped_duration"]
    veh_speed = RAIN_INTENSITY[rain_type]["veh_speed"]
    print(f"Detected Rainfall Intensity: {rain_type.upper()} → Ped Duration: {ped_time}s, Vehicle Speed: {veh_speed} m/s")

    # ==== Modify vehicle route file ====
    vehicle_file = os.path.join(BASELINE_SCENARIO, "vehicles.rou.xml")
    output_vehicle_file = os.path.join(RAIN_SCENARIO, "vehicles.rou.xml")
    tree = ET.parse(vehicle_file)
    for vType in tree.findall(".//vType"):
        vType.set("maxSpeed", str(veh_speed))  # adjust vehicle speed for safety
    tree.write(output_vehicle_file)

    # ==== Modify pedestrian file ====
    pedestrian_file = os.path.join(BASELINE_SCENARIO, "pedestrians.rou.xml")
    output_pedestrian_file = os.path.join(RAIN_SCENARIO, "pedestrians.rou.xml")
    tree = ET.parse(pedestrian_file)
    root = tree.getroot()

    for person in root.findall(".//person"):
        walk = person.find("walk")
        if walk is not None:
            walk.set("duration", str(ped_time))  # give longer crossing time

    tree.write(output_pedestrian_file)
    print(f" Rain-adaptive scenario generated in: {RAIN_SCENARIO}")

if __name__ == "__main__":
    generate_rain_adaptive_scenario()
