-- used to add countries, returns country ids
CREATE OR REPLACE PROCEDURE work_scraper.add_countries(
    country_codes TEXT[], OUT country_ids INTEGER[]
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- inserting missing countries
    -- filtering out null values
    WITH filter_nulls AS (
        SELECT DISTINCT c.cc
        FROM unnest(country_codes) AS c(cc)
        WHERE c.cc IS NOT NULL
    )
    -- inserting non null countries
    INSERT INTO work_scraper.countries (country_code)
    SELECT cc FROM filter_nulls
    ON CONFLICT DO NOTHING;

    -- selecting country ids from country_codes, while leaving null values as null
    SELECT ARRAY(
        SELECT c.id
        FROM unnest(country_codes) WITH ORDINALITY AS input(cc, ord) -- to keep correct order
        -- left join to keep nulls
        LEFT JOIN work_scraper.countries c ON c.country_code = input.cc
        ORDER BY ord
    )
    INTO country_ids;
END;
$$;