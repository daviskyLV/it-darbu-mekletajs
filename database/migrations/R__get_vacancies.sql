-- returns X amount of vacancies starting from skip_amount offset
-- based on provided source, whether they're fully checked and expiration time
CREATE OR REPLACE FUNCTION work_scraper.get_vacancies(
    source TEXT,
    -- amount INTEGER,
    -- skip_amount INTEGER,
    include_expired BOOLEAN,
    employers INTEGER[],
    min_salary DOUBLE PRECISION,
    max_salary DOUBLE PRECISION,
    salary_hourly BOOLEAN,
    remote_job BOOLEAN,
    max_age INTERVAL,
    countries INTEGER[],
    cities INTEGER[]
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
    expiration_filter TIMESTAMP;
    publishing_filter TIMESTAMP := now() - max_age;
    employers_filter INTEGER[];
    countries_filter INTEGER[];
    cities_filter INTEGER[];
BEGIN
    SELECT work_scraper.get_website_id(source) INTO source_id;
    -- handling invalid source input
    IF NOT FOUND THEN
        RETURN;
    END IF;

    IF include_expired = TRUE THEN
        -- includes expired vacancies
        expiration_filter := timestamp 'epoch';
    ELSE
        expiration_filter := now();
    END IF;
    
    IF cardinality(employers) = 0 THEN
        -- employers filter empty, including all employers
        SELECT id INTO employers_filter
        FROM work_scraper.employers;
    ELSE
        employers_filter := employers;
    END IF;
    
    IF cardinality(countries) = 0 THEN
        -- countries filter empty, including all countries
        SELECT id INTO countries_filter
        FROM work_scraper.countries;
    ELSE
        countries_filter := countries;
    END IF;

    IF cardinality(cities) = 0 THEN
        -- cities filter empty, including all cities
        SELECT id INTO cities_filter
        FROM work_scraper.cities;
    ELSE
        cities_filter := cities;
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
        AND v.expires > expiration_filter
        AND v.published >= publishing_filter
        AND (v.employer IS NULL OR v.employer = ANY(employers_filter))
        AND (v.country IS NULL OR v.country = ANY(countries_filter))
        AND (v.city IS NULL OR v.city = ANY(cities_filter))
        AND (v.is_hourly_rate IS NULL OR v.is_hourly_rate = salary_hourly)
        AND (v.remote IS NULL OR v.remote = remote_job)
        AND (
            (v.salary_min IS NULL OR v.salary_max IS NULL) OR
            (v.salary_max >= min_salary AND v.salary_max <= max_salary)
            )
    ORDER BY v.id ASC;
    --LIMIT amount OFFSET skip_amount;
END;
$$;