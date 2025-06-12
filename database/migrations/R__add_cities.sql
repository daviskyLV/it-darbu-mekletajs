-- used to add cities, returns city ids
CREATE OR REPLACE PROCEDURE work_scraper.add_cities(
    cities TEXT[], OUT city_ids INTEGER[]
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- inserting missing cities
    -- filtering out null values
    WITH filter_nulls AS (
        SELECT DISTINCT c.city_name
        FROM unnest(cities) AS c(city_name)
        WHERE c.city_name IS NOT NULL
    )
    -- inserting non null cities
    INSERT INTO work_scraper.cities (city_name)
    SELECT city_name FROM filter_nulls
    ON CONFLICT DO NOTHING;

    -- selecting city ids from titles, while leaving null values as null
    SELECT ARRAY(
        SELECT c.id
        FROM unnest(cities) WITH ORDINALITY AS input(city_name, ord) -- to keep correct order
        -- left join to keep nulls
        LEFT JOIN work_scraper.cities c ON c.city_name = input.city_name
        ORDER BY ord
    )
    INTO city_ids;
END;
$$;