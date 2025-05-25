# IT darbu meklētājs / IT job searcher
This is a small web-scraper program that looks through popular job listing websites in the Latvian job market. It mainly searches for IT related jobs, but can be modified to fit the needs for other categories.

## How it works
1. Each site has a dedicated `Python` script that scrapes the website and saves information about a job if it meets the criteria
2. The job is further analysed and saved in `PostgreSQL` database
3. Steps 1 and 2 run in parallel to gather data faster
4. Each site has its own `Dockerfile` for the scripts, so they can be run in separate containers
5. `PostgreSQL` database is expected to be a single instance

More in-depth documentation about the system can be found in code documentation and system documentation.

## Installation
==[TODO]==

## Useful info
Results regarding IT jobs can be seen on my [website](https://www.davisky.lv/it-darbi)
