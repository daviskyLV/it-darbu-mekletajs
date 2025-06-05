# IT darbu meklētājs / IT job searcher
This is a small web-scraper program that looks through popular job listing websites in the Latvian job market. It mainly searches for IT related jobs, but can be modified to fit the needs for other categories.

## Technical requirements
1. Docker
2. Docker compose

## Installation
### Base/local installation
1. Clone the repository via `git clone https://github.com/daviskyLV/it-darbu-mekletajs.git`
2. Navigate to [it-darbu-mekletajs/settings/](/settings/)
3. Copy [template.env](/settings/template.env) and rename it to `.env`
4. Fill out the fields in `.env` so the scrapers can connect to database
5. (Optional) Edit [keywords.json](/settings/keywords.json) with your desired keywords to search for
6. Run [setup.py](/settings/setup.py) via `python setup.py` to set up all scraper folders
7. Navigate to [it-darbu-mekletajs/database/](/database/) and follow README.md for database installation
8. After running the database, navigate to [scrapers directory](/scrapers/)
9. Either run [compose.yaml](/scrapers/compose.yaml) to run all scrapers on a single machine or build and run each scraper's **Docker image** and run them on separate machines.

### Additional notes
1. If you change [scrapers/utils](/scrapers/utils/) code, remember to adjust the [utils Dockerfile](/scrapers/utils/Dockerfile) and build and upload your own image
2. If using a custom **utils** image, remember to change the base image in each scraper's `Dockerfile`

## Useful info
Results regarding IT jobs can be seen on my [website](https://www.davisky.lv/it-darbi) (TODO)
