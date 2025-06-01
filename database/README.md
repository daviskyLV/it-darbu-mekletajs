# Database DDL, Stored Functions and Stored Procedures
For the scripts to work, the database tables and functions/procedures must be set up. Additionally, it is important to understand how the `vacancies` table `summarized_description` column JSONB is formatted. An example formation can be found in `summarized_description.json`.

## Scraper interface
The scripts shouldn't have access to modify/read table data directly and should only use these functions/procedures:
1. `work_scraper.website_is_stale` - This **function** should be used to check whether the website domain vacancy list needs to be refetched.
2. `work_scraper.mark_website_scanning` - this **procedure** should be used when the scraper decides to rescan the whole list.
3. `work_scraper.add_vacancies` - this **procedure** should be used when the scraper has refetched the vacancy list and wants to add vacancy information to the table.
4. `work_scraper.get_stale_vacancies` - this **function** should be used when the scraper wants to get out of date vacancies. The procedure reserves these vacancies for the scraper for 2 hours.
5. `work_scraper.update_vacancies` - this **procedure** should be used when the scraper wants to update an already EXISTING vacancy.

## Installation
Make sure to have PostgreSQL 17 or later installed, some older versions might work too.
1. execute `tables.sql` to add the necessary tables and their indexes to the database. Optionally, manually add their owner and restrictions.
2. execute `get_website_id.sql` to add the internally used **function**.
3. execute `add_cities.sql`, `add_countries.sql` and `add_employers.sql` to add the internally used **procedures**, which populate the cities, countries and employers tables.
4. execute `website_is_stale.sql` and `mark_website_scanning.sql` to add the corresponding **function/procedure**.
5. execute `add_vacancies.sql`, `get_stale_vacancies.sql` and `update_vacancies.sql` to allow the scripts to work with the `vacancies` table.