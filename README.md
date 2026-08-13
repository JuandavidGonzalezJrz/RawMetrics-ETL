# RawMetrics-ETL

RawMetrics-ETL is a Python-based ETL project for extracting and cleaning time-series telemetry from `.FIT` activity files.

The project focuses on preserving the temporal structure of sensor data while applying domain-aware cleaning rules to cycling telemetry such as power, cadence, heart rate, speed, temperature, and other metrics available in FIT `record` messages.

## Current Pipeline

```text
.FIT File
    ↓
FITExtractor
    ↓
Raw Pandas DataFrame
    ↓
Telemetry Cleaning
    ↓
Clean Time-Series DataFrame
```

The current implementation covers the **extraction** and **cleaning** stages of the pipeline.

## Features

### FIT Telemetry Extraction

`extractor.py`:

* Parses `.FIT` files using `fitparse`.
* Filters FIT `record` messages containing activity telemetry.
* Dynamically extracts all available fields instead of relying on a fixed metric list.
* Converts records into a structured Pandas `DataFrame`.
* Converts FIT timestamps into a `DatetimeIndex` for time-series operations.

### Domain-Aware Telemetry Cleaning

`cleaner.py` applies cycling-specific rules rather than treating all missing values identically.

#### Coasting normalization

When cadence is zero, power is explicitly normalized to zero:

```text
cadence == 0 → power = 0
```

This preserves legitimate zero-power periods such as descending or coasting.

#### Power dropout detection

A missing power value is considered a candidate sensor dropout when the rider is actively pedaling:

```text
cadence > 0 AND power is NaN
```

#### Time-based interpolation

Detected power dropouts are reconstructed using time-based linear interpolation.

The current strategy:

* Interpolates only the `power` series.
* Uses the timestamp index for temporal interpolation.
* Limits interpolation to a maximum of 5 consecutive missing readings.
* Interpolates only gaps bounded by valid observations.
* Applies reconstructed values only to rows identified as active-pedaling power dropouts.

This prevents legitimate zero-power values from being overwritten by synthetic data.

## Project Structure

```text
RawMetrics-ETL/
│
├── extractor.py       # FIT parsing and raw DataFrame generation
├── cleaner.py         # Domain-aware telemetry cleaning
├── .gitignore
└── README.md
```

## Technology Stack

* **Python**
* **Pandas**
* **fitparse**
* **Git / GitHub**

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd RawMetrics-ETL
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install pandas fitparse
```

## Usage

Place a `.FIT` activity file locally in the project directory.

FIT files are intentionally excluded from version control through `.gitignore`.

The extraction stage creates a time-indexed DataFrame from the telemetry contained in the file:

```python
from extractor import FITExtractor

extractor = FITExtractor("training.fit")
extractor.extract_raw_data()
df_raw = extractor.to_dataframe()
```

The cleaning stage can then be applied to the extracted telemetry:

```python
from cleaner import telemetry_clean

df_clean = telemetry_clean(df_raw)
```

## Design Principles

The project follows several data-engineering principles:

* **Preserve temporal alignment** by using timestamps as the DataFrame index.
* **Separate missing data from legitimate zero values.**
* **Apply domain knowledge before statistical reconstruction.**
* **Avoid indiscriminate interpolation across valid sensor states.**
* **Keep parsing and cleaning responsibilities separated into independent modules.**

## Current Status

### Completed

* [x] FIT file parsing
* [x] Dynamic extraction of `record` telemetry
* [x] Timestamp-based indexing
* [x] Coasting normalization
* [x] Power dropout detection
* [x] Bounded time-based interpolation
* [x] Modular extraction and cleaning stages

### Planned

* [ ] Telemetry processing and derived metrics
* [ ] Export layer
* [ ] Pipeline orchestration through `main.py`
* [ ] Automated tests
* [ ] Additional validation and data-quality checks

## Project Goal

RawMetrics-ETL is being developed as a modular telemetry-processing pipeline capable of transforming raw endurance-sport sensor data into structured and reliable datasets suitable for downstream analytics and future data-engineering workflows.

The project prioritizes data integrity, explicit domain rules, and maintainable pipeline architecture over indiscriminate preprocessing.
