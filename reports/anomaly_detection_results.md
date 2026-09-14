# Anomaly Detection Results

## 1. Objective

The objective of the anomaly detection component is to identify abnormal sensor behavior in the IoT condition monitoring dataset.

The detector combines:

- Rule-based data quality checks
- Statistical anomaly detection
- Rolling-window features
- Context-aware features
- Isolation Forest
- Hybrid anomaly detection logic

The final evaluation is performed at the sensor measurement level using:

`(timestamp, device_id, sensor)`

---

## 2. Dataset and Ground Truth

The synthetic dataset contains:

- 10 devices
- 5 locations
- 30 days
- 1-minute sampling frequency
- 5 sensors per device

The resulting dataset contains:

**432,000 sensor measurements**

The ground-truth anomaly file contains **1,690 anomaly records**.

The anomaly types are:

| Anomaly Type | Ground Truth Records |
|---|---:|
| Stuck | 600 |
| Missing | 500 |
| Drift | 500 |
| Impossible Value | 50 |
| Spike | 40 |
| **Total** | **1,690** |

Because multiple anomaly records can refer to the same
`(timestamp, device_id, sensor)` evaluation point, the 1,690 ground-truth records correspond to **1,689 unique evaluation points**.

Therefore, model evaluation is based on unique evaluation keys rather than raw ground-truth record count.

---

## 3. Detection Results

The final hybrid detector identified:

**914 sensor-level detections**

The detected anomalies were classified using the detector's primary detection reason.

| Detection Reason | Detections |
|---|---:|
| Missing | 500 |
| Stuck | 314 |
| Spike | 100 |
| Drift | 0 |
| Impossible | 0 |
| **Total** | **914** |

The final detector successfully identifies missing values and several spike and stuck-sensor patterns.

However, the current detector does not successfully identify the injected drift and impossible-value anomalies in the final detection output.

---

## 4. Overall Model Performance

The evaluation is performed at the unique
`(timestamp, device_id, sensor)` level.

| Metric | Value |
|---|---:|
| True Positives | 901 |
| False Positives | 13 |
| False Negatives | 788 |
| True Negatives | 2,158,298 |
| Precision | 98.58% |
| Recall | 53.35% |
| F1 Score | 69.23% |

### Interpretation

The detector has very high precision.

When the model reports an anomaly, it is usually correct.

However, recall is substantially lower than precision. This means that the detector misses a considerable number of true anomalies.

The F1 score reflects this trade-off between precision and recall.

The results therefore indicate that the current detector is conservative: it produces relatively few false alarms but fails to detect a significant portion of the injected anomalies.

---

## 5. Performance by Sensor

Model performance varies substantially across sensors.

| Sensor | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Temperature | 520 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| CO2 | 19 | 0 | 1 | 100.00% | 95.00% | 97.44% |
| Humidity | 362 | 9 | 287 | 97.57% | 55.78% | 70.98% |
| Airspeed | 0 | 1 | 500 | 0.00% | 0.00% | 0.00% |
| Light | 0 | 3 | 0 | 0.00% | 0.00% | 0.00% |

### Interpretation

#### Temperature

Temperature is the strongest-performing sensor.

All 520 unique ground-truth anomaly points were detected, with no false positives.

#### CO2

CO2 also performs very well.

The detector identifies 19 of the 20 unique ground-truth anomaly points.

#### Humidity

Humidity represents the main source of missed anomalies among the successfully detected sensor types.

Although precision remains high at 97.57%, recall is only 55.78%.

This indicates that the detector is reliable when it raises an alert, but it misses many humidity anomalies.

#### Airspeed

The detector fails to identify the injected airspeed drift anomalies.

All 500 unique airspeed ground-truth anomaly points are missed.

This is an important limitation of the current feature and detection strategy.

#### Light

There are no ground-truth light anomalies in the dataset.

The three light detections are therefore false positives.

Consequently, recall is not meaningful as a measure of anomaly detection capability for light in this dataset; the observed value is 0% because there are no true positive anomaly points.

---

## 6. Anomaly-Type Analysis

The ground-truth anomaly distribution contains five anomaly types:

- Stuck
- Missing
- Drift
- Impossible Value
- Spike

The detector does not detect all anomaly types equally well.

### Missing

Missing temperature values are detected successfully.

The final detector identifies all 500 missing-anomaly records represented at the evaluation level.

### Stuck

The detector identifies a substantial portion of the stuck-sensor anomalies, particularly the humidity stuck pattern.

### Spike

The detector identifies a number of injected spike anomalies across several sensors.

### Drift

The current detector does not successfully detect the injected drift pattern.

The main example is the airspeed drift injected into DEV_007.

This suggests that the current feature set and thresholding strategy are insufficient for detecting this gradual behavioral change.

### Impossible Value

The ground truth contains 50 impossible-value anomaly records.

However, the final detection output does not contain any detections classified with the `impossible` reason.

This indicates that the current final hybrid detection pipeline should be improved if impossible-value detection is a project requirement.

---

## 7. Main Findings

The final model demonstrates several important characteristics:

1. **High precision**

   The model achieves 98.58% precision and therefore produces relatively few false alarms.

2. **Moderate overall recall**

   Recall is 53.35%, meaning that a substantial proportion of true anomaly points remain undetected.

3. **Strong temperature performance**

   Temperature anomalies are detected completely in the current dataset.

4. **Strong CO2 performance**

   CO2 achieves 95% recall and 97.44% F1.

5. **Moderate humidity performance**

   Humidity achieves 55.78% recall while maintaining 97.57% precision.

6. **Poor drift detection**

   The current detector fails to identify the injected airspeed drift anomalies.

7. **No successful impossible-value detections in the final output**

   The final detection pipeline should be improved if this anomaly type must be reliably detected.

8. **Sensor-specific performance matters**

   A single overall metric does not adequately describe detector behavior across all sensors.

---

## 8. Limitations

The results should be interpreted in the context of the synthetic dataset.

### Synthetic Data

The dataset is simulated and therefore cannot fully reproduce the complexity of real industrial IoT environments.

### Synthetic Ground Truth

The anomaly patterns and their locations were intentionally injected.

Real-world anomalies may have different magnitudes, durations, temporal structures, and relationships with operating conditions.

### Class Imbalance

Normal measurements greatly outnumber anomalous measurements.

Therefore, accuracy is not an appropriate primary metric for evaluating this detector.

Precision, recall, and F1 are more informative for this task.

### Detector Limitations

The current hybrid detector is much stronger for some anomaly patterns than others.

In particular, gradual drift remains difficult to detect.

### Threshold Sensitivity

Statistical and machine-learning anomaly detectors depend on threshold selection.

Different thresholds would change the precision-recall trade-off.

### Evaluation Grain

Ground-truth records are not necessarily unique evaluation points.

For this reason, evaluation uses unique:

`(timestamp, device_id, sensor)`

keys.

---

## 9. Future Improvements

Potential improvements include:

- Dedicated drift detection using rolling regression or change-point detection
- Explicit rule-based impossible-value detection
- Sensor-specific thresholds
- More context-aware features
- Adaptive thresholds based on operating conditions
- Longer temporal windows for slow anomalies
- Cross-sensor contextual features
- Time-series models for sequential anomaly detection
- Evaluation on real-world labeled IoT data
- Threshold optimization based on operational cost
- Separate detection strategies for different anomaly types

---

## 10. Final Assessment

The current detector provides a useful baseline for an end-to-end IoT condition monitoring system.

Its main strength is high precision, while its main weakness is incomplete anomaly coverage.

The results demonstrate why anomaly detection in IoT systems should not be evaluated using a single aggregate metric.

Sensor-specific behavior, anomaly type, temporal characteristics, and operational context all affect detection performance.

The current system should therefore be considered a baseline anomaly detection pipeline rather than a production-ready anomaly detection solution.