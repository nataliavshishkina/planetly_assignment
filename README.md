# Setting up the data

* Init DB and `Global_Land_Temperatures_By_City` table (defined using Django ORM):
  * `python manage.py makemigrations`
  * `python manage.py migrate`

* Upload data from the downloaded CSV to the created table:
    * `./upload_csv.sh `
    * Internally this script calls `transform_csv.py` to converts the CSV to the internal fromat (basically it converts latitudes and longitude to standard format) and then uploads it to DB by using `COPY` command in `psql`.
    * `COPY` command is the fastest way to make a bulk upload. I've also tried `bulk_crteate()` method Django ORM, but it froze my system.

# API implementation details

Note, all requests attached here are generated by Postman and use cURL CLI.

* Create new entry
  * Strightforward implementation using ModelViewSet od the Django REST framework
  * As bonus it implemenets additional standard entrypoints for the entries which can be useful during frontend development
```
curl --location --request POST 'http://127.0.0.1:8000/api/temperature_entries/' \
--header 'Content-Type: application/json' \
--data-raw '{ "date": "2013-06-01", "average_temperature": 15.043, "average_temperature_uncertainity": 0.261, "city": "Zwolle", "country": "Netherlands", "latitude": 52.24, "longitude": 5.26 }'
```

* Update existing entry by date and city
  * Since `(date, city)` is not a uniqe entry identifier we have to add an option to use any additional filters (e.g. country or latitude)
  * Also we perform a basic uniquness check before updating entry
  * Alternative option was to introduce `(date, city, country)` constraint in DB, but it ended up that there are 2 Haicheng cities in China.
  * A proper approach would be to create a separate table for cities and refernce it by a foreign index from the entries table.
  * To speedup this method we could add an index for the `Global_Land_Temperatures_By_City` table.
```
curl --location --request PUT 'http://127.0.0.1:8000/api/temperature_entries/update_by_date_and_city/' \
--header 'Content-Type: application/json' \
--data-raw '{ "date": "2013-06-01", "city": "Zwolle",  "average_temperature": 15.043, "average_temperature_uncertainity": 0.261 }'
```

* Get top N cities with highest monthly temperature in `[from; to]` date range:
  * Implemented as 2 subseqent queries using Django ORM.
  * The first query fetches id with the max temperature for each city. The second query reads rows with these ids and find top N.
```
curl --location --request GET 'http://127.0.0.1:8000/api/top_cities/10/from/2010-01-01/to/2010-12-31/'
```

# API excercies

### a. Find the entry whose city has the highest AverageTemperature since the year 2000.

Request: 
```
curl --location --request GET 'http://127.0.0.1:8000/api/top_cities/1/from/2000-01-01/to/2099-12-31/'
```

Response: 
```
[
    {
        "id": 17315436,
        "date": "2013-07-01",
        "average_temperature": 39.15600000000001,
        "average_temperature_uncertainity": 0.37,
        "city": "Ahvaz",
        "country": "Iran",
        "latitude": 31.35,
        "longitude": 49.01
    }
]
```

### b. Following above: assume the temperature observation of the city last month breaks the record. It is 0.1 degree higher with the same uncertainty. Create this entry

Request:
```
curl --location --request POST 'http://127.0.0.1:8000/api/temperature_entries/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "date": "2021-10-01",
    "average_temperature": 39.25600000000001,
    "average_temperature_uncertainity": 0.37,
    "city": "Ahvaz",
    "country": "Iran",
    "latitude": 31.35,
    "longitude": 49.01
}'
```

Response: 
```
{
    "id": 25797639,
    "date": "2021-10-01",
    "average_temperature": 39.25600000000001,
    "average_temperature_uncertainity": 0.37,
    "city": "Ahvaz",
    "country": "Iran",
    "latitude": 31.35,
    "longitude": 49.01
}
```

### c. Following question 1: assume the returned entry has been found erroneous. The actual average temperature of this entry is 2.5 degrees lower. Update this entry.

Request:
```
curl --location --request PUT 'http://127.0.0.1:8000/api/temperature_entries/update_by_date_and_city/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "date": "2021-10-01",
    "average_temperature": 36.75600000000001,
    "average_temperature_uncertainity": 0.37,
    "city": "Ahvaz",
    "country": "Iran"
}'
```

Response:
```
{
    "id": 25797639,
    "date": "2021-10-01",
    "average_temperature": 36.75600000000001,
    "average_temperature_uncertainity": 0.37,
    "city": "Ahvaz",
    "country": "Iran",
    "latitude": 31.35,
    "longitude": 49.01
}
```

