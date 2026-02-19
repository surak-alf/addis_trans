# Addis_Transit_Sim

[![SUMO Version](https://img.shields.io/badge/SUMO-1.25.0-blue)](https://www.eclipse.org/sumo/)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)

`addis_trans` is a Python-based traffic and public transit simulation project focusing on **Addis Ababa, Ethiopia**. It utilizes the **SUMO (Simulation of Urban MObility)** suite to model urban transportation dynamics by integrating real-world geographic data and public transit schedules.

## 🚀 Features

* **SUMO Integration:** Complete simulation configurations (`.sumocfg`) and vehicle type definitions (`vtypes.xml`) optimized for the Addis Ababa road network.
* **Public Transit Modeling:** Supports **GTFS** (General Transit Feed Specification) integration for realistic bus and transit scheduling.
* **Geospatial Accuracy:** Incorporates **OpenStreetMap (OSM)** data to reflect the specific topology and infrastructure of the city.
* **Automated Workflow:** Python-based scripts to manage TraCI connections, process Floating Car Data (FCD), and automate simulation runs.
* **RL Ready:** Structured to support Reinforcement Learning environments for traffic signal control or transit optimization.

---

## 📁 Project Structure

The repository is organized to separate simulation logic from raw data and generated outputs:

```text
Addis_Transit_Sim/
├── gtfs/                 # Public transit schedule data (GTFS format)
├── osm/                  # OpenStreetMap source files and network conversions
├── scripts/              # Python scripts for data processing and TraCI management
├── sumo_files/           # Core configuration files (.net.xml, .rou.xml, .sumocfg)
├── resources/            # Additional assets, stops, and passenger definitions
├── outputs/              # Simulation results and logs (Ignored by Git)
└── README.md


## 🛠 Getting Started

### Prerequisites
* **SUMO:** [Download and Install SUMO](https://sumo.dlr.de/docs/Installing/index.html). Ensure the `SUMO_HOME` environment variable is set.
* **Python 3.8+:** Required for running the automation scripts and TraCI interface.

### Installation
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/surak-alf/addis_trans.git](https://github.com/surak-alf/addis_trans.git)
   cd addis_trans