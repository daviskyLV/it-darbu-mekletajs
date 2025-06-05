-- checks whether a website job vacancy list is stale, aka the list should be refetched
CREATE OR REPLACE FUNCTION work_scraper.website_is_stale(source TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    last_updated TIMESTAMP;
    currently_scanning BOOLEAN;
    stale BOOLEAN := FALSE;
BEGIN
    SELECT status_updated, scanning
    INTO last_updated, currently_scanning
    FROM work_scraper.sources
    WHERE website = source;

    -- timed out scanning staleness
    IF last_updated IS NULL OR currently_scanning IS NULL THEN
        -- source not found
        stale := FALSE;
    ELSIF currently_scanning = FALSE AND now() >= last_updated + INTERVAL '3 days' THEN
        -- website isnt currently getting scanned and its been 3 days since last scan
        stale := TRUE;
    ELSIF currently_scanning = TRUE AND now() >= last_updated + INTERVAL '2 hours' THEN
        -- website is currently marked as scanned, but hasnt received any updates in a while
        -- marking as stale
        stale := TRUE;
    END IF;

    RETURN stale;
END;
$$;