-- Used to add a list of vacancies that exist, but haven't been fully checked
CREATE OR REPLACE PROCEDURE work_scraper.add_unscanned_vacancies(
    web_id TEXT[],
    source TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    source_id INTEGER;
BEGIN
    SELECT work_scraper.get_website_id(source) INTO source_id;

    -- inserting vacancy ids for source
    INSERT INTO work_scraper.unscanned_vacancies (vacancy_web_id, web_source)
    SELECT inp.wid, source_id
    FROM unnest(web_id) AS inp(wid)
    -- making sure that the vacancy with the same web id doesnt already exist
    LEFT JOIN work_scraper.vacancies v
        ON v.vacancy_web_id = inp.wid AND v.web_source = source_id
    WHERE v.vacancy_web_id IS NULL
    ON CONFLICT DO NOTHING;
END;
$$;