#!/bin/bash
set -e

# Transform CSV from Kaggle to internal format
python3 transform_csv.py -i "GlobalLandTemperaturesByCity.csv" -o "GlobalLandTemperaturesByCity_transformed.csv"

export PGPASSWORD=example
export POSTGRES_HOST=${POSTGRES_HOST:=localhost}

# Truncate existing rows in GlobalLandTemperaturesByCity table
psql -h "$POSTGRES_HOST" -U postgres -c "SELECT COUNT(1) FROM global_land_temperatures_by_city;"
psql -h "$POSTGRES_HOST" -U postgres -c "TRUNCATE TABLE global_land_temperatures_by_city;"

# Insert new rows from CSV
psql -h "$POSTGRES_HOST" -U postgres -c "\copy global_land_temperatures_by_city (date,average_temperature,average_temperature_uncertainity,city,country,latitude,longitude) FROM 'GlobalLandTemperaturesByCity_transformed.csv' WITH (FORMAT CSV, HEADER);"
psql -h "$POSTGRES_HOST" -U postgres -c "SELECT COUNT(1) FROM global_land_temperatures_by_city;"
