# IT darbu meklētājs / IT job searcher
This is a small web-scraper program that looks through popular job listing websites in the Latvian job market. It mainly searches for IT related jobs, but can be modified to fit the needs for other categories.

## Technical requirements
1. Python 3.11+ (with pip)
2. PostgreSQL 17+ (might work on earlier versions)
3. (Optional) Docker for running in a container

## Installation
1. Clone the repository via `git clone https://github.com/daviskyLV/it-darbu-mekletajs.git`
2. Navigate to [it-darbu-mekletajs/settings/](/settings/)
3. Copy [template.env](/settings/template.env) and rename it to `.env`
4. Fill out the fields in `.env` so the scrapers can connect to database
5. (Optional) Edit [keywords.json](/settings/keywords.json) with your desired keywords to search for
6. Run [setup.py](/settings/setup.py) via `python setup.py` to set up all scraper folders
7. Navigate to [it-darbu-mekletajs/database/](/database/) and follow README.md for database installation
8. To run the scrapers, either launch each of them in their own container using the provided Dockerfile or create a virtual environment for each and run `scraper.py`

## Useful info
Results regarding IT jobs can be seen on my [website](https://www.davisky.lv/it-darbi) (TODO)
