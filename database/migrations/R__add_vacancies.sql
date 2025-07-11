-- used to add several brand new vacancies
CREATE OR REPLACE PROCEDURE work_scraper.add_vacancies(
    title TEXT[],
    employer TEXT[],
    salary_min DOUBLE PRECISION[],
    salary_max DOUBLE PRECISION[],
    is_hourly BOOLEAN[],
    remote BOOLEAN[],
    published TIMESTAMP[],
    expires TIMESTAMP[],
    country_code TEXT[],
    city_name TEXT[],
    web_id TEXT[],
    source TEXT,
    description TEXT[],
    summarized JSONB[]
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    curtime TIMESTAMP := now();
    emp_ids INTEGER[];
    country_ids INTEGER[];
    city_ids INTEGER[];
    source_id INTEGER;
BEGIN
    SELECT work_scraper.get_website_id(source) INTO source_id;
    CALL work_scraper.add_employers(employer, emp_ids);
    CALL work_scraper.add_countries(country_code, country_ids);
    CALL work_scraper.add_cities(city_name, city_ids);

    -- inserting vacancies
    INSERT INTO work_scraper.vacancies (
        title, employer, salary_min, salary_max, is_hourly_rate, remote,
        published, expires, country, city, last_checked, vacancy_web_id,
        web_source, description, summarized_description
    )
    -- converting parameter column arrays and procedure variables to table
    SELECT
        title[i],
        emp_ids[i],
        salary_min[i],
        salary_max[i],
        is_hourly[i],
        remote[i],
        published[i],
        expires[i],
        country_ids[i],
        city_ids[i],
        curtime,
        web_id[i],
        source_id,
        description[i],
        summarized[i]
    FROM generate_subscripts(title, 1) AS i -- positional index for alignment
    ON CONFLICT DO NOTHING;
END;
$$;