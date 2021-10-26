import argparse
import pandas as pd


CSV_COLUMN_NAMES_TO_DB_NAMES = {
    "dt": "date",
    "AverageTemperature": "average_temperature",
    "AverageTemperatureUncertainty": "average_temperature_uncertainity",
    "City": "city",
    "Country": "country",
    "Latitude": "latitude",
    "Longitude": "longitude",
}


def main():
    parser = argparse.ArgumentParser(description='Converts CSV from Kaggle to internal format suitable for Postgres COPY command')
    parser.add_argument('-i', type=str, required=True)
    parser.add_argument('-o', type=str, required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.i)
    df.rename(columns=CSV_COLUMN_NAMES_TO_DB_NAMES, inplace=True)

    # Standirtize latitude and longitude
    def transform_latitude(csv_latitude):
        if not csv_latitude:
            return None
        return (1 if csv_latitude[-1] == 'N' else -1) * float(csv_latitude[:-1])

    def transform_longitude(csv_longitude):
        if not csv_longitude:
            return None
        return (1 if csv_longitude[-1] == 'E' else -1) * float(csv_longitude[:-1])

    df["latitude"] = df["latitude"].map(transform_latitude)
    df["longitude"] = df["longitude"].map(transform_longitude)

    df.to_csv(args.o, index=False)


if __name__ == "__main__":
    main()
