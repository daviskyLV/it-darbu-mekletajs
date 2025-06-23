-- Only used temporarily while inserting new, not fully processed vacancies
CREATE TABLE work_scraper.unscanned_vacancies(
    id              SERIAL
                    CONSTRAINT unscanned_vacancies_pk PRIMARY KEY,
    vacancy_web_id  TEXT NOT NULL,
    web_source      INTEGER NOT NULL
                    CONSTRAINT web_source_fk REFERENCES work_scraper.sources,
    last_checked    TIMESTAMP DEFAULT timestamp 'epoch'
);

CREATE INDEX last_checked_index
ON work_scraper.unscanned_vacancies (last_checked);

CREATE UNIQUE INDEX source_web_id_index
ON work_scraper.unscanned_vacancies (web_source, vacancy_web_id);