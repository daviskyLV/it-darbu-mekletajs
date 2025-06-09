-- returns all cities in database
CREATE OR REPLACE FUNCTION work_scraper.get_cities()
RETURNS TABLE(
    db_id INTEGER,
    city_name TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.city_name
    FROM work_scraper.cities c
    ORDER BY c.id ASC;
END;
$$;