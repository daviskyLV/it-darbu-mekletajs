# Database DDL, Stored Functions and Stored Procedures
For the scripts to work, the database tables and functions/procedures must be set up. Additionally, it is important to understand how the `vacancies` table `summarized_description` column JSONB is formatted. An example formation can be found in `summarized_description.json`.

## Scraper interface
The scripts shouldn't have access to modify/read table data directly and should only use these functions/procedures:
1. `work_scraper.website_is_stale` - This **function** should be used to check whether the website domain vacancy list needs to be refetched.
2. `work_scraper.mark_website_scanning` - this **procedure** should be used when the scraper decides to rescan the whole list.
3. `work_scraper.add_vacancies` - this **procedure** should be used when the scraper has refetched the vacancy list and wants to add vacancy information to the table.
4. `work_scraper.get_stale_vacancies` - this **function** should be used when the scraper wants to get out of date vacancies. The procedure reserves these vacancies for the scraper for 2 hours.
5. `work_scraper.update_vacancies` - this **procedure** should be used when the scraper wants to update an already EXISTING vacancy.
6. `work_scraper.delete_vacancies` - this **procedure** should be used when the scraper detects that the vacancy doesn't meet the requirements and should be deleted.
7. `work_scraper.get_vacancies` - this **function** can be used to retrieve vacancies from the database (country, city, employer, etc. names need to be retrieved separately).
8. `work_scraper.get_countries` - this **function** can be used to retrieve all countries in the database with their corresponding Ids.
9. `work_scraper.get_cities` - this **function** can be used to retrieve all cities in the database with their corresponding Ids.
10. `work_scraper.get_employers` - this **function** can be used to retrieve all employers in the database with their corresponding Ids.

## Installation
1. Make sure to have **Docker compose** installed
2. Edit the `.env` file to specify database admin and scraper user credentials, as well as other parameters
3. Run `docker compose up --build` to start up the database and automatically apply all updates