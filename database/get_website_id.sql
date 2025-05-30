-- gets website id from domain name
CREATE OR REPLACE FUNCTION work_scraper.get_website_id(source TEXT)
RETURNS INTEGER
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    web_id INTEGER;
BEGIN
    SELECT id INTO web_id
    FROM work_scraper.sources
    WHERE website = source;

    RETURN web_id;
END;
$$;