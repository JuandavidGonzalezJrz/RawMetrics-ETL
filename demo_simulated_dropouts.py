import pandas as pd

from cleaner import telemetry_clean

timestamps = pd.date_range(
    start="2026-08-13 12:00:00",
    periods=5,
    freq="1s",
)

df_raw = pd.DataFrame(
    {
        "power": [200.0, 210.0, float("nan"), 230.0, float("nan")],
        "cadence": [85.0, 86.0, 87.0, 88.0, 0.0],
    },
    index=timestamps,
)

df_clean = telemetry_clean(df_raw.copy())

print("---- SIMULATED RAW DATA ----")
print(df_raw)

print("\n---- CLEAN DATA ----")
print(df_clean)
