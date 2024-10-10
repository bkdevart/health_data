# Health Analysis
Data summarization scripts and dashboards focused around smart watch data.

## Overview
Data was collected on Apple watch models over various years. Initial analysis focused on bicycle exercise data.

## Analysis
<!--<iframe src="https://bkdevart.github.io/health_data/"></iframe>-->

Preliminary findings

- Regular cycling path is apparent in histogram of cycling distances, with 5.6 miles accounting for 46% of the exercises

[Dashboard link](https://bkdevart.github.io/health_data/)

## Setup notes

Export your data from the Apple health app, and extract the compressed file to a folder inside this repo named `apple_health_export`. The preprocess script will export data to a folder named `cleaned_data`.

### Docker commands

To get the docker environment up and running, you'll need to use the following commands:

```bash
docker compose up
docker compose down
```

For using the database:

```bash
docker compose run --rm postgres psql -h health_data-postgres_health-1 -U health_db -d health_db
```
