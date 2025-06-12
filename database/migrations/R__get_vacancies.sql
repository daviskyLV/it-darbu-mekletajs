-- returns X amount of vacancies starting from skip_amount offset
-- based on provided source, whether they're fully checked and expiration time
CREATE OR REPLACE FUNCTION work_scraper.get_vacancies(
    source TEXT, amount INTEGER, skip_amount INTEGER,
    fully_checked BOOLEAN, include_expired BOOLEAN
)
RETURNS TABLE(
    db_id INTEGER,
    title TEXT,
    employer_id INTEGER,
    salary_min DOUBLE PRECISION,
    salary_max DOUBLE PRECISION,
    is_hourly_rate BOOLEAN,
    remote BOOLEAN,
    published TIMESTAMP,
    expires TIMESTAMP,
    country_id INTEGER,
    city_id INTEGER,
    vacancy_web_id TEXT,
    description TEXT,
    summarized_description JSONB
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    source_id INTEGER;
    last_check_filter TIMESTAMP;
    expiration_filter TIMESTAMP;
BEGIN
    SELECT work_scraper.get_website_id(source) INTO source_id;
    IF fully_checked = TRUE THEN
        -- vacancies must be fully checked (unchecked have epoch timestamp)
        last_check_filter := timestamp 'epoch' + INTERVAL '1 second';
    ELSE
        last_check_filter := timestamp 'epoch';
    END IF;
    IF include_expired = TRUE THEN
        -- includes expired vacancies
        expiration_filter := timestamp 'epoch';
    ELSE
        last_check_filter := now();
    END IF;

    -- handling invalid source input
    IF NOT FOUND THEN
        RETURN;
    END IF;

    RETURN QUERY
    SELECT
        v.id,
        v.title,
        v.employer,
        v.salary_min,
        v.salary_max,
        v.is_hourly_rate,
        v.remote,
        v.published,
        v.expires,
        v.country,
        v.city,
        v.vacancy_web_id,
        v.description,
        v.summarized_description
    FROM work_scraper.vacancies v
    WHERE v.web_source = source_id
        AND v.last_checked >= last_check_filter
        AND v.expires > expiration_filter
    ORDER BY v.id ASC
    LIMIT amount OFFSET skip_amount;
END;
$$;