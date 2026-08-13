import pandas as pd

from extractor import FITExtractor


def validate_zero_cadence(df):
    """Zeroes out power output when coasting (cadence = 0) to eliminate sensor
    artifacts."""

    df.loc[df["cadence"] == 0, "power"] = 0.0
    return df


def handle_dropouts(df):
    """Linearly interpolates up to 5 consecutive NaN power readings (1 Hz) during
    active pedaling."""

    df = df.asfreq(
        "1s",
    )
    identified_interruptions = (df["cadence"] > 0) & (df["power"].isna())
    restored_power = df["power"].interpolate(
        method="time", limit=5, limit_area="inside"
    )
    df.loc[identified_interruptions, "power"] = restored_power.loc[
        identified_interruptions
    ]

    return df


def telemetry_clean(df):
    """Consolidates cadence-based zeroing and power interpolation into a single
    cleaning pipeline."""

    df = validate_zero_cadence(df)
    df = handle_dropouts(df)

    return df


if __name__ == "__main__":
    extractor = FITExtractor("training.fit")
    extractor.extract_raw_data()
    df_raw = extractor.to_dataframe()

    df_clean = telemetry_clean(df_raw)

    # Convert speed metrics from m/s to km/h for standard reporting
    df_clean["enhanced_speed"] = df_clean["enhanced_speed"] * 3.6
    df_raw["enhanced_speed"] = df_raw["enhanced_speed"] * 3.6

    # Extract target time range relative to initial timestamp for segment analysis
    time_to_try_clean = df_clean.index.min()
    time_lapse_clean = df_clean.loc[
        time_to_try_clean + pd.Timedelta(minutes=0) : time_to_try_clean
        + pd.Timedelta(minutes=0, seconds=5)
    ]
    time_to_try_raw = df_raw.index.min()
    time_lapse_raw = df_raw.loc[
        time_to_try_raw + pd.Timedelta(minutes=0) : time_to_try_raw
        + pd.Timedelta(minutes=0, seconds=5)
    ]

    # Filter target metrics and remove fully unpopulated records
    print("---- RAW DATA ----")
    print(
        time_lapse_raw[
            ["power", "cadence", "heart_rate", "temperature", "enhanced_speed"]
        ]
        .dropna(
            how="all",
        )
        .head()
    )

    # Filter target metrics and remove fully unpopulated records
    print("----  CLEAN DATA  ----")
    print(
        time_lapse_clean[
            ["power", "cadence", "heart_rate", "temperature", "enhanced_speed"]
        ]
        .dropna(
            how="all",
        )
        .head()
    )
