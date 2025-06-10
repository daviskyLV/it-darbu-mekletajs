# IT darbu meklētājs / IT job searcher
This is a small web-scraper program that looks through popular job listing websites in the Latvian job market. It mainly searches for IT related jobs, but can be modified to fit the needs for other categories.

## Technical requirements
1. Docker
2. Docker compose
3. Linux

## Installation
1. Clone the repository via `git clone https://github.com/daviskyLV/it-darbu-mekletajs.git`
2. Navigate to [it-darbu-mekletajs/settings/](/settings/)
3. Edit the database environment variables in [database.env](settings/database.env), admin user being priviledged user and scrapers user being the one meant for scrapers
4. Edit the scrapers environment variables in [scrapers.env](settings/scrapers.env), make sure to match scraper user credentials with the database env vars
5. (Optional) Edit [keywords.json](/settings/keywords.json) with your desired keywords to search for
6. Run [setup.py](/settings/setup.py) via `python setup.py` to set up configurations in scraper and database folders
7. Navigate to [it-darbu-mekletajs/database/](/database/) and follow README.md for database installation
8. After running the database, navigate to [scrapers directory](/scrapers/)
9. Run `docker compose up --build` to run all scrapers on a single machine

### Additional notes
1. If you change [scrapers/utils](/scrapers/utils/) code, remember to adjust the [utils Dockerfile](/scrapers/utils/Dockerfile) and build and upload your own image
2. If using a custom **utils** image, remember to change the base image in each scraper's `Dockerfile`

## Useful info
Results regarding IT jobs can be seen on my [website](https://www.davisky.lv/it-darbi) (TODO)
