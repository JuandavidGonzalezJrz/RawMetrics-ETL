import pandas as pd
from fitparse import FitFile
from pandas import DataFrame


class FITExtractor:
    """Extracts second-by-second sensor telemetry from Garmin/Wahoo .FIT files
    into structured Pandas DataFrames for RawMetrics-ETL."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_fit = FitFile(file_path)
        self.records_data = []

    def extract_raw_data(self):
        for message in self.file_fit:
            # Filter second-by-second telemetry records; ignore metadata and pauses
            if message.name == "record":
                minibox_data = {}
                for record_data in message:
                    minibox_data[record_data.name] = record_data.value

                self.records_data.append(minibox_data)

    def to_dataframe(self):
        """Parses raw timestamps into a DatetimeIndex to enable time-series operations.
        Replaces the default RangeIndex to allow efficient temporal slicing and resampling."""

        raw_databox = pd.DataFrame(self.records_data)
        raw_databox["timestamp"] = pd.to_datetime(raw_databox["timestamp"])
        raw_databox.set_index("timestamp", inplace=True)

        return raw_databox


if __name__ == "__main__":
    ()

# extractor is the name robot
extractor = FITExtractor("training.fit")
extractor.extract_raw_data()
df_final = extractor.to_dataframe()

df_final["enhanced_speed"] = df_final["enhanced_speed"] * 3.6

time_to_try = df_final.index.min()

time_lapse = df_final.loc[
    time_to_try + pd.Timedelta(minutes=52) : time_to_try
    + pd.Timedelta(minutes=52, seconds=20)
]


# print("Columnas extraidas")
# print(df_final.columns.tolist())


print("Muestra de metricas principales:")
print(
    time_lapse[["power", "cadence", "heart_rate", "temperature", "enhanced_speed"]]
    .dropna(
        subset=["power", "cadence", "heart_rate", "temperature", "enhanced_speed"],
        how="all",
    )
    .head()
)
