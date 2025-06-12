-- sets the scanning [for listings] status for a website
CREATE OR REPLACE PROCEDURE work_scraper.mark_website_scanning(source TEXT, scanning_status BOOLEAN)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE work_scraper.sources
    SET scanning = scanning_status, status_updated = now()
    WHERE website = source;
END;
$$;