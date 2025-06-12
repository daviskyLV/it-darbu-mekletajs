-- returns all countries in the database
CREATE OR REPLACE FUNCTION work_scraper.get_countries()
RETURNS TABLE(
    db_id INTEGER,
    country_code TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.country_code
    FROM work_scraper.countries c
    ORDER BY c.id ASC;
END;
$$;