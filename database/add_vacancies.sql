-- used to add several brand new vacancies
CREATE OR REPLACE PROCEDURE work_scraper.add_vacancies(
    title TEXT[], employer TEXT[],
    salary_min DOUBLE PRECISION[], salary_max DOUBLE PRECISION[],
    is_hourly BOOLEAN[], remote BOOLEAN[],
    published TIMESTAMP[], expires TIMESTAMP[],
    country_code VARCHAR(8)[], city_name TEXT[],
    full_info BOOLEAN[], web_id TEXT[], source TEXT,
    description TEXT[], summarized JSONB[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    curtime TIMESTAMP := now();
    checked_times TIMESTAMP[];
    emp_ids INTEGER[];
    country_ids INTEGER[];
    city_ids INTEGER[];
    source_id INTEGER;
BEGIN
    SELECT get_website_id(source) INTO source_id;
    CALL work_scraper.add_employers(employer, emp_ids);
    CALL work_scraper.add_countries(country_code, country_ids);
    CALL work_scraper.add_cities(city_name, city_ids);
    -- converting full_info to either epoch time (needs rechecking) or now()
    SELECT ARRAY(
        SELECT CASE
            WHEN input.fi IS NULL OR input.fi = 0 THEN timestamp 'epoch'
            ELSE curtime
        END
        FROM unnest(full_info) WITH ORDINALITY AS input(fi, ord) -- to keep correct order
        ORDER BY ord
    )
    INTO checked_times;


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
        checked_times[i],
        web_id[i],
        source_id,
        description[i],
        summarized[i]
    FROM generate_subscripts(title, 1) AS i -- positional index for alignment
    ON CONFLICT DO NOTHING;
END;
$$;