from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42

N_DEVICES = 10
N_DAYS = 30
FREQUENCY = "1min"

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
GROUND_TRUTH_DIR = DATA_DIR / "ground_truth"

RAW_FILE = RAW_DIR / "iot_sensor_data.csv"
GROUND_TRUTH_FILE = GROUND_TRUTH_DIR / "anomalies.csv"


def create_timestamps():
    """Create the common timestamp index."""
    return pd.date_range(
        start="2026-01-01",
        periods=N_DAYS * 24 * 60,
        freq=FREQUENCY,
    )


def create_device_metadata():
    """Create device and spatial metadata."""
    locations = {
        "LOC_A": (0, 0),
        "LOC_B": (10, 0),
        "LOC_C": (0, 10),
        "LOC_D": (10, 10),
        "LOC_E": (5, 5),
    }

    metadata = []

    for device_number in range(1, N_DEVICES + 1):
        location_index = (device_number - 1) // 2
        location_name = list(locations.keys())[location_index]

        x, y = locations[location_name]

        metadata.append(
            {
                "device_id": f"DEV_{device_number:03d}",
                "location_id": location_name,
                "x": x,
                "y": y,
            }
        )

    return pd.DataFrame(metadata)


def generate_normal_data():
    """Generate realistic baseline sensor measurements."""
    rng = np.random.default_rng(SEED)

    timestamps = create_timestamps()
    metadata = create_device_metadata()

    frames = []

    for device in metadata.itertuples(index=False):
        minutes = np.arange(len(timestamps))

        # Daily cycle: approximately one 24-hour period.
        daily_cycle = np.sin(2 * np.pi * minutes / (24 * 60))

        # Slowly varying environmental component.
        slow_cycle = np.sin(2 * np.pi * minutes / (7 * 24 * 60))

        # Device-specific baseline.
        device_offset = rng.normal(0, 0.6)

        temperature = (
            24
            + 3.5 * daily_cycle
            + 0.8 * slow_cycle
            + device_offset
            + rng.normal(0, 0.25, len(minutes))
        )

        humidity = (
            65
            - 8 * daily_cycle
            - 1.5 * slow_cycle
            - device_offset
            + rng.normal(0, 1.0, len(minutes))
        )

        # CO2 tends to increase when ventilation/environmental
        # conditions become less favorable.
        co2 = (
            800
            + 180 * (-daily_cycle)
            + 60 * slow_cycle
            + rng.normal(0, 20, len(minutes))
        )

        airspeed = 0.35 + 0.08 * daily_cycle + rng.normal(0, 0.015, len(minutes))

        light = 50 + 40 * np.maximum(daily_cycle, 0) + rng.normal(0, 3, len(minutes))

        frame = pd.DataFrame(
            {
                "timestamp": timestamps,
                "device_id": device.device_id,
                "location_id": device.location_id,
                "temperature": temperature,
                "humidity": humidity,
                "co2": co2,
                "airspeed": airspeed,
                "light": light,
                "x": device.x,
                "y": device.y,
            }
        )

        frames.append(frame)

    data = pd.concat(frames, ignore_index=True)

    data["production_day"] = (data["timestamp"] - data["timestamp"].min()).dt.days + 1

    return data


def inject_anomalies(data):
    """Inject realistic sensor anomalies and return ground truth."""
    rng = np.random.default_rng(SEED + 1)

    anomalies = []

    # 1. Temperature spikes
    for _ in range(20):
        index = rng.integers(0, len(data))

        data.loc[index, "temperature"] += rng.uniform(8, 15)

        anomalies.append(
            {
                "row_index": index,
                "timestamp": data.loc[index, "timestamp"],
                "device_id": data.loc[index, "device_id"],
                "sensor": "temperature",
                "anomaly_type": "spike",
            }
        )

    # 2. CO2 spikes
    for _ in range(20):
        index = rng.integers(0, len(data))

        data.loc[index, "co2"] += rng.uniform(800, 1500)

        anomalies.append(
            {
                "row_index": index,
                "timestamp": data.loc[index, "timestamp"],
                "device_id": data.loc[index, "device_id"],
                "sensor": "co2",
                "anomaly_type": "spike",
            }
        )

    # 3. Stuck humidity sensor
    for _ in range(5):
        # device = rng.choice(data["device_id"].unique())
        # start = rng.integers(0, len(data) - 120)

        # device_indices = data.index[data["device_id"] == device]

        # selected_indices = device_indices[start : start + 120]
        device = rng.choice(data["device_id"].unique())

        device_indices = data.index[data["device_id"] == device]

        start = rng.integers(
            0,
            len(device_indices) - 120,
        )

        selected_indices = device_indices[start : start + 120]
        # /////////////////////////////////////////////////////////////
        stuck_value = data.loc[selected_indices[0], "humidity"]

        data.loc[selected_indices, "humidity"] = stuck_value

        for index in selected_indices:
            anomalies.append(
                {
                    "row_index": index,
                    "timestamp": data.loc[index, "timestamp"],
                    "device_id": data.loc[index, "device_id"],
                    "sensor": "humidity",
                    "anomaly_type": "stuck",
                }
            )

    # 4. Missing temperature values
    missing_indices = rng.choice(
        len(data),
        size=500,
        replace=False,
    )

    data.loc[missing_indices, "temperature"] = np.nan

    for index in missing_indices:
        anomalies.append(
            {
                "row_index": index,
                "timestamp": data.loc[index, "timestamp"],
                "device_id": data.loc[index, "device_id"],
                "sensor": "temperature",
                "anomaly_type": "missing",
            }
        )

    # 5. Impossible humidity values
    impossible_indices = rng.choice(
        len(data),
        size=50,
        replace=False,
    )

    data.loc[impossible_indices, "humidity"] = rng.uniform(
        101,
        130,
        size=len(impossible_indices),
    )

    for index in impossible_indices:
        anomalies.append(
            {
                "row_index": index,
                "timestamp": data.loc[index, "timestamp"],
                "device_id": data.loc[index, "device_id"],
                "sensor": "humidity",
                "anomaly_type": "impossible_value",
            }
        )

    # 6. Airspeed drift
    device = "DEV_007"

    device_indices = data.index[data["device_id"] == device]

    drift_indices = device_indices[-500:]

    drift = np.linspace(
        0,
        0.25,
        len(drift_indices),
    )

    data.loc[drift_indices, "airspeed"] += drift

    for index in drift_indices:
        anomalies.append(
            {
                "row_index": index,
                "timestamp": data.loc[index, "timestamp"],
                "device_id": data.loc[index, "device_id"],
                "sensor": "airspeed",
                "anomaly_type": "drift",
            }
        )

    ground_truth = pd.DataFrame(anomalies)

    return data, ground_truth


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)

    data = generate_normal_data()
    data, ground_truth = inject_anomalies(data)

    data.to_csv(RAW_FILE, index=False)
    ground_truth.to_csv(GROUND_TRUTH_FILE, index=False)

    print(f"Dataset created: {RAW_FILE}")
    print(f"Shape: {data.shape}")

    print(f"Ground truth created: {GROUND_TRUTH_FILE}")
    print(f"Anomalies: {len(ground_truth)}")


if __name__ == "__main__":
    main()
