-- returns all employers in database
CREATE OR REPLACE FUNCTION work_scraper.get_employers()
RETURNS TABLE(
    db_id INTEGER,
    title TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.title
    FROM work_scraper.employers e
    ORDER BY e.id ASC;
END;
$$;