from pathlib import Path

import numpy as np
import pandas as pd


# Project paths
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
GROUND_TRUTH_DIR = DATA_DIR / "ground_truth"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_FILE = RAW_DIR / "iot_sensor_data.csv"
GROUND_TRUTH_FILE = GROUND_TRUTH_DIR / "anomalies.csv"

MEASUREMENTS_FILE = PROCESSED_DIR / "sensor_measurements.csv"
ANOMALIES_FILE = PROCESSED_DIR / "sensor_anomalies.csv"
DEVICE_SUMMARY_FILE = PROCESSED_DIR / "device_summary.csv"
LOCATION_SUMMARY_FILE = PROCESSED_DIR / "location_summary.csv"

SENSOR_COLUMNS = [
    "temperature",
    "humidity",
    "co2",
    "airspeed",
    "light",
]


def load_data():
    """Load raw sensor data and ground-truth anomaly data."""
    measurements = pd.read_csv(RAW_FILE)
    ground_truth = pd.read_csv(GROUND_TRUTH_FILE)

    measurements["timestamp"] = pd.to_datetime(measurements["timestamp"])

    ground_truth["timestamp"] = pd.to_datetime(ground_truth["timestamp"])

    return measurements, ground_truth


def prepare_measurements(measurements):
    """Prepare the clean measurement fact table."""
    columns = [
        "timestamp",
        "device_id",
        "location_id",
        "temperature",
        "humidity",
        "co2",
        "airspeed",
        "light",
        "x",
        "y",
        "production_day",
    ]

    result = measurements[columns].copy()

    result = result.sort_values(["timestamp", "device_id"]).reset_index(drop=True)

    return result


def prepare_anomalies(measurements, ground_truth):
    """Create a long-format sensor-level anomaly table."""
    anomaly_keys = ground_truth[
        [
            "timestamp",
            "device_id",
            "sensor",
            "anomaly_type",
        ]
    ].drop_duplicates()

    device_locations = measurements[
        [
            "device_id",
            "location_id",
        ]
    ].drop_duplicates()

    anomaly_keys = anomaly_keys.merge(
        device_locations,
        on="device_id",
        how="left",
    )

    anomaly_keys["is_anomaly"] = True

    columns = [
        "timestamp",
        "device_id",
        "location_id",
        "sensor",
        "anomaly_type",
        "is_anomaly",
    ]

    result = anomaly_keys[columns].copy()

    result = result.sort_values(["timestamp", "device_id", "sensor"]).reset_index(
        drop=True
    )

    return result


def prepare_device_summary(measurements, anomalies):
    """Create device-level monitoring summary."""
    summary = (
        measurements.groupby("device_id")
        .agg(
            location_id=("location_id", "first"),
            measurement_count=("timestamp", "size"),
            first_timestamp=("timestamp", "min"),
            last_timestamp=("timestamp", "max"),
        )
        .reset_index()
    )

    anomaly_counts = (
        anomalies.groupby("device_id").size().rename("anomaly_count").reset_index()
    )

    summary = summary.merge(
        anomaly_counts,
        on="device_id",
        how="left",
    )

    summary["anomaly_count"] = summary["anomaly_count"].fillna(0).astype(int)

    summary["anomaly_rate"] = summary["anomaly_count"] / summary["measurement_count"]

    return summary.sort_values("device_id").reset_index(drop=True)


def prepare_location_summary(measurements, anomalies):
    """Create location-level monitoring summary."""
    summary = (
        measurements.groupby("location_id")
        .agg(
            device_count=("device_id", "nunique"),
            measurement_count=("timestamp", "size"),
            first_timestamp=("timestamp", "min"),
            last_timestamp=("timestamp", "max"),
        )
        .reset_index()
    )

    anomaly_counts = (
        anomalies.groupby("location_id").size().rename("anomaly_count").reset_index()
    )

    summary = summary.merge(
        anomaly_counts,
        on="location_id",
        how="left",
    )

    summary["anomaly_count"] = summary["anomaly_count"].fillna(0).astype(int)

    summary["anomaly_rate"] = summary["anomaly_count"] / summary["measurement_count"]

    return summary.sort_values("location_id").reset_index(drop=True)


def validate_outputs(
    measurements,
    anomalies,
    device_summary,
    location_summary,
):
    """Validate the generated analytics tables."""
    assert len(measurements) > 0
    assert len(anomalies) > 0

    assert measurements["timestamp"].notna().all()
    assert measurements["device_id"].notna().all()
    assert measurements["location_id"].notna().all()

    assert anomalies["is_anomaly"].eq(True).all()

    assert (
        anomalies[["timestamp", "device_id", "sensor", "anomaly_type"]]
        .duplicated()
        .sum()
        == 0
    )

    assert set(anomalies["sensor"]).issubset(set(SENSOR_COLUMNS))

    assert device_summary["device_id"].is_unique
    assert location_summary["location_id"].is_unique


def save_outputs(
    measurements,
    anomalies,
    device_summary,
    location_summary,
):
    """Save analytics-ready datasets."""
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    measurements.to_csv(
        MEASUREMENTS_FILE,
        index=False,
    )

    anomalies.to_csv(
        ANOMALIES_FILE,
        index=False,
    )

    device_summary.to_csv(
        DEVICE_SUMMARY_FILE,
        index=False,
    )

    location_summary.to_csv(
        LOCATION_SUMMARY_FILE,
        index=False,
    )


def main():
    measurements, ground_truth = load_data()

    sensor_measurements = prepare_measurements(measurements)

    sensor_anomalies = prepare_anomalies(
        measurements,
        ground_truth,
    )

    device_summary = prepare_device_summary(
        sensor_measurements,
        sensor_anomalies,
    )

    location_summary = prepare_location_summary(
        sensor_measurements,
        sensor_anomalies,
    )

    validate_outputs(
        sensor_measurements,
        sensor_anomalies,
        device_summary,
        location_summary,
    )

    save_outputs(
        sensor_measurements,
        sensor_anomalies,
        device_summary,
        location_summary,
    )

    print("Analytics data preparation completed.")
    print()
    print(
        "sensor_measurements:",
        sensor_measurements.shape,
    )
    print(
        "sensor_anomalies:",
        sensor_anomalies.shape,
    )
    print(
        "device_summary:",
        device_summary.shape,
    )
    print(
        "location_summary:",
        location_summary.shape,
    )


if __name__ == "__main__":
    main()
from pathlib import Path

import numpy as np
import pandas as pd


# Project paths
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
GROUND_TRUTH_DIR = DATA_DIR / "ground_truth"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_FILE = RAW_DIR / "iot_sensor_data.csv"
GROUND_TRUTH_FILE = GROUND_TRUTH_DIR / "anomalies.csv"

MEASUREMENTS_FILE = PROCESSED_DIR / "sensor_measurements.csv"
ANOMALIES_FILE = PROCESSED_DIR / "sensor_anomalies.csv"
DEVICE_SUMMARY_FILE = PROCESSED_DIR / "device_summary.csv"
LOCATION_SUMMARY_FILE = PROCESSED_DIR / "location_summary.csv"

SENSOR_COLUMNS = [
    "temperature",
    "humidity",
    "co2",
    "airspeed",
    "light",
]


def load_data():
    """Load raw sensor data and ground-truth anomaly data."""
    measurements = pd.read_csv(RAW_FILE)
    ground_truth = pd.read_csv(GROUND_TRUTH_FILE)

    measurements["timestamp"] = pd.to_datetime(measurements["timestamp"])

    ground_truth["timestamp"] = pd.to_datetime(ground_truth["timestamp"])

    return measurements, ground_truth


def prepare_measurements(measurements):
    """Prepare the clean measurement fact table."""
    columns = [
        "timestamp",
        "device_id",
        "location_id",
        "temperature",
        "humidity",
        "co2",
        "airspeed",
        "light",
        "x",
        "y",
        "production_day",
    ]

    result = measurements[columns].copy()

    result = result.sort_values(["timestamp", "device_id"]).reset_index(drop=True)

    return result


def prepare_anomalies(measurements, ground_truth):
    """Create a long-format sensor-level anomaly table."""
    anomaly_keys = ground_truth[
        [
            "timestamp",
            "device_id",
            "sensor",
            "anomaly_type",
        ]
    ].drop_duplicates()

    device_locations = measurements[
        [
            "device_id",
            "location_id",
        ]
    ].drop_duplicates()

    anomaly_keys = anomaly_keys.merge(
        device_locations,
        on="device_id",
        how="left",
    )

    anomaly_keys["is_anomaly"] = True

    columns = [
        "timestamp",
        "device_id",
        "location_id",
        "sensor",
        "anomaly_type",
        "is_anomaly",
    ]

    result = anomaly_keys[columns].copy()

    result = result.sort_values(["timestamp", "device_id", "sensor"]).reset_index(
        drop=True
    )

    return result


def prepare_device_summary(measurements, anomalies):
    """Create device-level monitoring summary."""
    summary = (
        measurements.groupby("device_id")
        .agg(
            location_id=("location_id", "first"),
            measurement_count=("timestamp", "size"),
            first_timestamp=("timestamp", "min"),
            last_timestamp=("timestamp", "max"),
        )
        .reset_index()
    )

    anomaly_counts = (
        anomalies.groupby("device_id").size().rename("anomaly_count").reset_index()
    )

    summary = summary.merge(
        anomaly_counts,
        on="device_id",
        how="left",
    )

    summary["anomaly_count"] = summary["anomaly_count"].fillna(0).astype(int)

    summary["anomaly_rate"] = summary["anomaly_count"] / summary["measurement_count"]

    return summary.sort_values("device_id").reset_index(drop=True)


def prepare_location_summary(measurements, anomalies):
    """Create location-level monitoring summary."""
    summary = (
        measurements.groupby("location_id")
        .agg(
            device_count=("device_id", "nunique"),
            measurement_count=("timestamp", "size"),
            first_timestamp=("timestamp", "min"),
            last_timestamp=("timestamp", "max"),
        )
        .reset_index()
    )

    anomaly_counts = (
        anomalies.groupby("location_id").size().rename("anomaly_count").reset_index()
    )

    summary = summary.merge(
        anomaly_counts,
        on="location_id",
        how="left",
    )

    summary["anomaly_count"] = summary["anomaly_count"].fillna(0).astype(int)

    summary["anomaly_rate"] = summary["anomaly_count"] / summary["measurement_count"]

    return summary.sort_values("location_id").reset_index(drop=True)


def validate_outputs(
    measurements,
    anomalies,
    device_summary,
    location_summary,
):
    """Validate the generated analytics tables."""
    assert len(measurements) > 0
    assert len(anomalies) > 0

    assert measurements["timestamp"].notna().all()
    assert measurements["device_id"].notna().all()
    assert measurements["location_id"].notna().all()

    assert anomalies["is_anomaly"].eq(True).all()

    assert (
        anomalies[["timestamp", "device_id", "sensor", "anomaly_type"]]
        .duplicated()
        .sum()
        == 0
    )

    assert set(anomalies["sensor"]).issubset(set(SENSOR_COLUMNS))

    assert device_summary["device_id"].is_unique
    assert location_summary["location_id"].is_unique


def save_outputs(
    measurements,
    anomalies,
    device_summary,
    location_summary,
):
    """Save analytics-ready datasets."""
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    measurements.to_csv(
        MEASUREMENTS_FILE,
        index=False,
    )

    anomalies.to_csv(
        ANOMALIES_FILE,
        index=False,
    )

    device_summary.to_csv(
        DEVICE_SUMMARY_FILE,
        index=False,
    )

    location_summary.to_csv(
        LOCATION_SUMMARY_FILE,
        index=False,
    )


def main():
    measurements, ground_truth = load_data()

    sensor_measurements = prepare_measurements(measurements)

    sensor_anomalies = prepare_anomalies(
        measurements,
        ground_truth,
    )

    device_summary = prepare_device_summary(
        sensor_measurements,
        sensor_anomalies,
    )

    location_summary = prepare_location_summary(
        sensor_measurements,
        sensor_anomalies,
    )

    validate_outputs(
        sensor_measurements,
        sensor_anomalies,
        device_summary,
        location_summary,
    )

    save_outputs(
        sensor_measurements,
        sensor_anomalies,
        device_summary,
        location_summary,
    )

    print("Analytics data preparation completed.")
    print()
    print(
        "sensor_measurements:",
        sensor_measurements.shape,
    )
    print(
        "sensor_anomalies:",
        sensor_anomalies.shape,
    )
    print(
        "device_summary:",
        device_summary.shape,
    )
    print(
        "location_summary:",
        location_summary.shape,
    )


if __name__ == "__main__":
    main()
