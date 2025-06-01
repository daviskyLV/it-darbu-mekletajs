-- used to update existing vacancies
CREATE OR REPLACE PROCEDURE work_scraper.update_vacancies(
    vacancy_id INTEGER[], title TEXT[], employer TEXT[],
    salary_min DOUBLE[], salary_max DOUBLE[],
    is_hourly BOOLEAN[], remote BOOLEAN[],
    published TIMESTAMP[], expires TIMESTAMP[],
    country_code VARCHAR(8)[], city_name TEXT[],
    full_info BOOLEAN[], description TEXT[], summarized JSONB[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    curtime TIMESTAMP := now();
    checked_times TIMESTAMP[];
    emp_ids INTEGER[];
    country_ids INTEGER[];
    city_ids INTEGER[];
BEGIN
    CALL work_scraper.add_employers(employer, emp_ids);
    CALL work_scraper.add_countries(country_code, country_ids);
    CALL work_scraper.add_cities(city_name, city_ids);
    -- converting full_info to either epoch time (needs rechecking) or now()
    SELECT ARRAY(
        SELECT CASE WHEN
            input.fi IS NULL OR input.fi = 0 THEN timestamp 'epoch'
            ELSE curtime
        END
        FROM unnest(full_info) WITH ORDINALITY AS input(fi, ord) -- to keep correct order
        ORDER BY ord
    )
    INTO checked_times;


    -- updating vacancies
    UPDATE work_scraper.vacancies AS l
    SET 
        title = inp.title,
        employer = inp.employer,
        salary_min = inp.salary_min,
        salary_max = inp.salary_max,
        is_hourly_rate = inp.is_hourly,
        remote = inp.remote,
        published = inp.published,
        expires = inp.expires,
        country = inp.country,
        city = inp.city,
        last_checked = inp.checked,
        description = inp.description,
        summarized_description = inp.summarized
    FROM (
        -- converting parameters and variables into an array
        SELECT
            vacancy_id[i] AS id,
            emp_ids[i] AS employer,
            salary_min[i] AS salary_min,
            salary_max[i] AS salary_max,
            is_hourly[i] AS is_hourly,
            remote[i] AS remote,
            published[i] AS published,
            expires[i] AS expires,
            country_ids[i] AS country,
            city_ids[i] AS city,
            checked_times[i] AS checked,
            description[i] AS description,
            summarized[i] AS summarized
        FROM generate_subscripts(vacancy_id, 1) AS i -- positional index for alignment
    ) AS inp
    WHERE l.id = inp.id;
END;
$$;