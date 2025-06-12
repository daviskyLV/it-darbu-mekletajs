# IT darbu meklētājs / IT job searcher
This is a small web-scraper program that looks through popular job listing websites in the Latvian job market. It mainly searches for IT related jobs, but can be modified to fit the needs for other categories.

## Technical requirements
1. Docker
2. Docker compose
3. Linux

## Installation
1. Clone the repository via `git clone https://github.com/daviskyLV/it-darbu-mekletajs.git`
2. Copy the `.env.template` file and rename it to `.env`
3. In the `.env` file fill out your desired database user credentials, `DB_ADMIN_USER` is meant for database's admin user, while `DB_SCRAPER_USER` is the user that the scrapers use to interface with the database
4. (Optional) Edit [keywords.json](/keywords.json) with your desired keywords to search for
5. Run `docker compose up --build` to start up the database and run all scrapers on a single machine

### Additional notes
1. For more information about the database read [database README.md](/database/README.md)
2. If you change [scrapers/utils](/scrapers/utils/) code, remember to adjust the [utils Dockerfile](/scrapers/utils/Dockerfile) and build and upload your own image
3. If using a custom **utils** image, remember to change the base image in each scraper's `Dockerfile`

## Useful info
Results regarding IT jobs can be seen on my [website](https://www.davisky.lv/it-darbi) (TODO)

## Licensing
Both [database](/database/) and [scrapers](/scrapers/) folders are under **GNU LGPL version 3** license (see more in the respective folders `LICENSE` files), while the rest is under [MIT](https://opensource.org/license/mit) license.