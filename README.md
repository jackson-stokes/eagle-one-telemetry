# ☕ Eagle One: Espresso Telemetry Dashboard

**Eagle One** is a containerized data engineering project that simulates, processes, and visualizes telemetry data from a Victoria Ardiuno Eagle One espresso machine.

It demonstrates an end-to-end data pipeline: generating synthetic sensor data with statistical drift, storing it via shared volumes, and visualizing real-time quality metrics using an interactive dashboard.

---

## 🚀 Features

* **Synthetic Data Generation**: Simulates realistic sensor noise (Pressure, Temperature, Extraction Time) and calculates a "Quality Score" algorithm based on deviation from ideal extraction targets.
* **Containerized Architecture**: Fully orchestrated using **Docker** and **Docker Compose** to separate the data engine from the presentation layer.
* **Interactive Visualization**: Built with **Streamlit** and **Plotly** to provide a reactive, web-based dashboard with:
    * Heatmap scatter plots for extraction precision.
    * Automated "Critical" and "Warning" status alerts.
    * Boiler temperature stability tracking.
* **Configurable Simulation**: All machine targets and physics variability are adjustable via `config.json`.

## 🛠️ Tech Stack

* **Infrastructure:** Docker, Docker Compose
* **Language:** Python 3.9
* **Data Processing:** Pandas, NumPy
* **Visualization:** Streamlit, Plotly Express
* **Configuration:** JSON

## 📂 Project Structure

```bash
├── config.json           # Simulation parameters & physics targets
├── dashboard.py          # Streamlit visualization application
├── data_generator.py     # Python script to generate mock sensor data
├── docker-compose.yml    # Orchestrates the Generator and Dashboard services
├── Dockerfile            # Blueprint for the Python environment
└── requirements.txt      # Python dependencies
```

## 🏁 Getting Started

### Prerequisites
* Docker Desktop installed on your machine.

### Installation & Run
1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/eagle-one-telemetry.git](https://github.com/YOUR_USERNAME/eagle-one-telemetry.git)
    cd eagle-one-telemetry
    ```

2.  **Build and Run with Docker Compose**:
    This command builds the image and spins up both the Data Generator and the Dashboard services.
    ```bash
    docker-compose up --build
    ```

3.  **Access the Dashboard**:
    Open your browser and navigate to:
    ```
    http://localhost:8501
    ```

## ⚙️ Configuration

[cite_start]You can tweak the simulation physics in `config.json` without changing the code.

**Example: Change the "Perfect Shot" definition:**
```json
"targets": {
    "pressure": 9.0,       // Change target pressure to 9 bars
    "temperature": 94.0,   // Increase target temp
    "extraction_time": 30.0
}
```
Note: If you change the config, restart the containers to apply changes.

## 📊 How it Works

The project consists of two isolated services sharing a Docker Volume:

1.  **`data_generator`**:
    * Reads `config.json`.
    * Generates `N` number of shots using NumPy normal distributions.
    * Calculates a calculated `quality_score` (0-10).
    * Writes to `eagle_one_cloud_data.csv` in the shared volume.

2.  **`dashboard`**:
    * Watches `eagle_one_cloud_data.csv`.
    * Calculates aggregate health metrics (Mean Pressure, Critical Count).
    * Renders charts using Plotly.
