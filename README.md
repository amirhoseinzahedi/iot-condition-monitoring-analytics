# IoT Condition Monitoring & Anomaly Detection

An end-to-end IoT analytics project for environmental condition monitoring,
data quality analysis, exploratory data analysis, anomaly detection,
and Power BI dashboarding.

The project uses a synthetic IoT dataset designed to simulate a
multi-device environmental monitoring system and demonstrates a complete
analytics workflow from raw sensor measurements to anomaly detection
and operational visualization.

## Project Overview

Environmental monitoring systems continuously collect measurements from
multiple sensors and devices. In practice, sensor data may contain missing
values, impossible readings, spikes, stuck sensors, or gradual drift.

This project demonstrates an end-to-end workflow to:

- Generate a realistic synthetic IoT monitoring dataset
- Evaluate sensor data quality
- Explore temporal, spatial, and device-level patterns
- Engineer features for anomaly detection
- Detect anomalous sensor behavior
- Evaluate detection performance against ground truth
- Prepare analytical datasets
- Visualize monitoring results in Power BI

The project focuses on the complete analytics workflow rather than
treating anomaly detection as an isolated machine learning task.

## Dataset

The project uses a synthetic IoT monitoring dataset.

| Attribute | Value |
|---|---:|
| Devices | 10 |
| Locations | 5 |
| Monitoring period | 30 days |
| Sampling frequency | 1 minute |
| Total measurements | 432,000 |
| Sensors per device | 5 |

### Sensors

- Temperature
- Humidity
- CO₂
- Air Speed
- Light

### Measurement Metadata

Each measurement contains:

- `timestamp`
- `device_id`
- `location_id`
- `x`
- `y`
- `production_day`

The generated data includes temporal patterns, device-specific
variation, spatial information, and measurement noise.

## Simulated Anomalies

The dataset contains intentionally injected anomalies that are stored
separately as ground truth for model evaluation.

The anomaly types are:

- Missing values
- Stuck sensor
- Spike
- Drift
- Impossible value

### Ground Truth Distribution

| Anomaly Type | Count |
|---|---:|
| Stuck | 600 |
| Missing | 500 |
| Drift | 500 |
| Impossible value | 50 |
| Spike | 40 |
| **Total** | **1,690** |

## Analytics Workflow

```text
Synthetic IoT Data
        |
        v
Data Quality Analysis
        |
        v
Exploratory Data Analysis
        |
        v
Feature Engineering
        |
        v
Anomaly Detection
        |
        v
Model Evaluation
        |
        v
Analytics Data Preparation
        |
        v
Power BI Dashboard
```

## Data Quality Analysis

The first stage evaluates the quality and reliability of the raw sensor
measurements before anomaly detection.

The analysis includes:

- Missing values and missing rates
- Duplicate records
- Duplicate logical keys
- Sensor value validity
- Timestamp intervals
- Sampling consistency
- Device-to-location relationships
- Coordinate consistency
- Sensor distributions

The project distinguishes between data quality issues and behavioral
anomalies.

For example:

- Missing values are treated as data quality issues.
- Impossible sensor values are treated as validity issues.
- Spikes, stuck behavior, and drift are treated as behavioral anomalies.

Notebook:

`notebooks/01_data_quality_analysis.ipynb`

## Exploratory Data Analysis

The EDA stage investigates how the monitoring system behaves across
time, devices, sensors, and locations.

The analysis includes:

- Descriptive statistics
- Sensor distributions
- Time-series analysis
- Hourly profiles
- Daily profiles
- Device comparison
- Location comparison
- Sensor correlation
- Temperature vs. humidity analysis
- Spatial analysis using device coordinates

Notebook:

`notebooks/02_exploratory_data_analysis.ipynb`

## Feature Engineering

The anomaly detection pipeline uses sensor-level and contextual features.

Examples include:

- Rolling mean
- Rolling standard deviation
- Rolling z-score
- Short-term differences
- Rolling slope
- Production day
- Time-of-day cyclic features

Rolling features are calculated separately for each device so that
recent device-specific behavior can be captured.

## Anomaly Detection

Several approaches are used in the anomaly detection pipeline.

### Rule-Based Detection

Domain-style rules identify clearly invalid sensor values, such as
measurements outside physically meaningful ranges.

### Statistical Detection

Rolling statistical features are used to identify unusual local
behavior, including sudden spikes and deviations from recent history.

### Isolation Forest

Isolation Forest is used as an unsupervised anomaly detection baseline.

The model operates on engineered sensor and contextual features and
produces an anomaly score for each observation.

### Hybrid Detector

The final detection approach combines rule-based and statistical signals
with the unsupervised model to produce sensor-level anomaly flags.

Notebook:

`notebooks/03_anomaly_detection.ipynb`

## Model Evaluation

The final detector is evaluated at the sensor-event level against the
ground-truth anomaly dataset.

### Final Results

| Metric | Result |
|---|---:|
| True Positives | 901 |
| False Positives | 13 |
| False Negatives | 788 |
| True Negatives | 2,158,298 |
| Precision | 98.58% |
| Recall | 53.35% |
| F1 Score | 69.23% |

> **Evaluation note:** The ground-truth file contains 1,690 anomaly records. Because some records refer to the same `(timestamp, device_id, sensor)` combination, these correspond to 1,689 unique evaluation points. Model evaluation therefore uses unique evaluation keys rather than raw ground-truth record count.

The detector achieves high precision, meaning that most reported
anomalies correspond to ground-truth anomalous sensor observations.

Recall is lower, meaning that a significant number of injected anomalies
were not detected.

This precision-recall trade-off is important in condition monitoring:
too many false alarms can reduce operational trust, while low recall can
allow important sensor problems to remain undetected.

The current detector should therefore be considered a baseline rather
than a production-ready anomaly detection system.

## Detection Results

The final hybrid detector produced **914 sensor-level detections**.

| Detection Reason | Count |
|---|---:|
| Missing | 500 |
| Stuck | 314 |
| Spike | 100 |
| Drift | 0 |
| Impossible | 0 |
| **Total** | **914** |

The detector successfully identifies missing values and several spike and stuck-sensor patterns.

However, the current detector does not successfully identify the injected drift and impossible-value anomalies in the final detection output.

These limitations are retained in the analysis rather than hidden,
because understanding model failure modes is an important part of
evaluating an anomaly detection system.

## Power BI Dashboard

The processed analytics data is visualized through an interactive
Power BI dashboard consisting of three analytical pages.

### Page 1 — Executive Overview

**Question: What is happening?**

Includes:

- Date, device, and location filters
- Detection KPIs
- Model KPIs
- Detection trend
- Detections by device
- Detections by reason
- Detections by sensor

### Page 2 — Operational Analysis

**Question: Where and when is it happening?**

Includes:

- Detections by device
- Detections by sensor and reason
- Detections by location
- Daily detection trend by location
- Ground-truth anomalies by location
- Spatial anomaly distribution

### Page 3 — Sensor & Anomaly Analysis

**Question: What is wrong, and how well does the detector identify it?**

Includes:

- Ground-truth anomalies by type
- Detection types by sensor
- Detection effectiveness by sensor
- Final model performance
- Confusion matrix
- Model performance by sensor
- Detection gap by anomaly type
- Recall by anomaly type

Power BI file:

`dashboard/dashboard.pbix`

## Analytics Data Preparation

The project includes a dedicated data preparation pipeline for
downstream analytics and Power BI.

Script:

`src/prepare_analytics_data.py`

The pipeline produces:

```text
data/processed/sensor_measurements.csv
data/processed/sensor_anomalies.csv
data/processed/device_summary.csv
data/processed/location_summary.csv
```

The final model detection results are also exported for dashboard
analysis.

## Project Structure

```text
iot-condition-monitoring-analytics/
|
├── data/
│   ├── raw/
│   ├── ground_truth/
│   └── sample/
|
├── notebooks/
│   ├── 01_data_quality_analysis.ipynb
│   ├── 02_exploratory_data_analysis.ipynb
│   └── 03_anomaly_detection.ipynb
|
├── src/
│   ├── generate_dataset.py
│   └── prepare_analytics_data.py
|
├── dashboard/
│   └── dashboard.pbix
|
├── reports/
|
├── .gitignore
├── README.md
└── requirements.txt
```

## Technologies

- Python
- Pandas
- NumPy
- Scikit-learn
- Jupyter Notebook
- Matplotlib
- Power BI
- DAX
- Git
- GitHub

## Reproducibility

### 1. Clone the repository

```bash
git clone <repository-url>
cd iot-condition-monitoring-analytics
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows with Git Bash:

```bash
source .venv/Scripts/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate the synthetic dataset

```bash
python src/generate_dataset.py
```

This generates the raw sensor data and ground-truth anomaly records.

### 5. Prepare analytics data

```bash
python src/prepare_analytics_data.py
```

### 6. Run the notebooks

Open the notebooks in the following order:

```text
01_data_quality_analysis.ipynb
02_exploratory_data_analysis.ipynb
03_anomaly_detection.ipynb
```

### 7. Open the Power BI dashboard

Open:

```text
dashboard/dashboard.pbix
```

Refresh the data sources if necessary.

## Data and Repository Policy

The project uses synthetic IoT data.

No proprietary, customer, production, or confidential company data is
required to reproduce the project.

Large generated datasets and processed CSV files are excluded from Git
using `.gitignore`.

The generation and processing scripts are included so that the analytical
workflow can be reproduced without committing large generated datasets.

## Limitations

### Synthetic Data

The dataset is simulated and does not represent the full complexity of
a production IoT environment.

### Ground Truth

Ground truth is generated from known injected anomalies. Real monitoring
systems typically require expert labeling, maintenance records, or other
reliable sources of truth.

### Detection Performance

The final detector has high precision but moderate recall:

- Precision: 98.58%
- Recall: 53.35%

This indicates that the detector is conservative: false alarms are relatively rare, but a significant portion of true anomalies remain undetected.

Performance also varies substantially across sensors, with particularly weak performance for the injected airspeed drift pattern.

### Anomaly Coverage

Some injected anomaly types are not successfully detected by the final
pipeline, particularly drift and impossible-value cases.

### Advanced Temporal and Spatial Modeling

The current implementation uses rolling and contextual features but does
not implement advanced multivariate temporal models or explicit
spatio-temporal anomaly detection.

## Future Improvements

Potential future improvements include:

- Improving drift detection
- Improving impossible-value detection
- Multivariate anomaly detection
- Device-specific baselines
- Location-aware anomaly models
- Online and streaming detection
- Threshold optimization based on operational costs
- Event-level and time-window-based evaluation
- Automated model monitoring
- Alert prioritization
- MQTT-based ingestion
- Production-oriented API deployment

## Key Takeaway

This project demonstrates an end-to-end IoT condition monitoring workflow:

```text
Data Generation
      |
      v
Data Quality
      |
      v
EDA
      |
      v
Feature Engineering
      |
      v
Anomaly Detection
      |
      v
Model Evaluation
      |
      v
Analytics Data Preparation
      |
      v
Power BI
```

The main objective is to demonstrate how raw sensor measurements can be
transformed into analytical insights while making both model performance
and model limitations visible.

## Key Findings

The final analysis produced several important findings:

- The detector achieved **98.58% precision**, indicating a low false-positive rate.
- Overall recall was **53.35%**, showing that many true anomaly points remain undetected.
- Temperature achieved **100% recall and 100% precision**.
- CO2 achieved **95% recall and 97.44% F1**.
- Humidity achieved **55.78% recall and 70.98% F1**.
- The detector failed to identify the injected airspeed drift anomaly pattern.
- No final detections were classified as `impossible`.
- Sensor-specific evaluation revealed substantially different detection behavior across sensors.
- The results demonstrate that a single aggregate metric is insufficient for evaluating an IoT anomaly detection system.
