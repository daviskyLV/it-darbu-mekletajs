CREATE SCHEMA IF NOT EXISTS work_scraper;

-- manually added in database, scanning status updated by scrapers
CREATE TABLE work_scraper.sources
(
    id              SERIAL
                    CONSTRAINT sources_pk PRIMARY KEY,
    website         TEXT NOT NULL,
    scanning        BOOLEAN DEFAULT FALSE, -- whether site's job listings (list) are currently being scanned 
    status_updated  TIMESTAMP DEFAULT timestamp 'epoch' -- last time status was changed
);

CREATE UNIQUE INDEX website_index
ON work_scraper.sources (website);

-- manually adding sources
INSERT INTO work_scraper.sources (website)
VALUES ('cv.lv');

-- populated by scrapers
CREATE TABLE work_scraper.employers
(
    id      SERIAL
            CONSTRAINT employers_pk PRIMARY KEY,
    title   TEXT NOT NULL
);

CREATE UNIQUE INDEX title_index
ON work_scraper.employers (title);

-- populated by scrapers
CREATE TABLE work_scraper.cities
(
    id          SERIAL
                CONSTRAINT cities_pk PRIMARY KEY,
    city_name   TEXT NOT NULL
);

CREATE UNIQUE INDEX cities_index
    ON work_scraper.cities (city_name);

-- populated by scrapers
CREATE TABLE work_scraper.countries
(
    id              SERIAL
                    CONSTRAINT countries_pk PRIMARY KEY,
    country_code    VARCHAR(8) NOT NULL
);

CREATE UNIQUE INDEX country_code_index
ON work_scraper.countries (country_code);

-- populated by scrapers
CREATE TABLE work_scraper.vacancies
(
    id                      SERIAL
                            CONSTRAINT vacancies_pk PRIMARY KEY,
    title                   TEXT,
    employer                INTEGER
                            CONSTRAINT employer_fk REFERENCES work_scraper.employers,
    salary_min              DOUBLE PRECISION,
    salary_max              DOUBLE PRECISION,
    is_hourly_rate          BOOLEAN,
    remote                  BOOLEAN,
    published               TIMESTAMP,
    expires                 TIMESTAMP,
    country                 INTEGER
                            CONSTRAINT country_fk REFERENCES work_scraper.countries,
    city                    INTEGER
                            CONSTRAINT city_fk REFERENCES work_scraper.cities,
    last_checked            TIMESTAMP DEFAULT timestamp 'epoch',
    vacancy_web_id          TEXT NOT NULL,
    web_source              INTEGER NOT NULL
                            CONSTRAINT web_source_fk REFERENCES work_scraper.sources,
    description             TEXT,
    summarized_description  jsonb
);

CREATE INDEX expires_index
ON work_scraper.vacancies (expires);

CREATE INDEX last_checked_index
ON work_scraper.vacancies (last_checked);

CREATE INDEX published_index
ON work_scraper.vacancies (published);

CREATE UNIQUE INDEX source_web_id_index
ON work_scraper.vacancies (web_source, vacancy_web_id);