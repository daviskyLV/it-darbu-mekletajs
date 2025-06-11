-- checks whether a website job vacancy list is stale, aka the list should be refetched
CREATE OR REPLACE FUNCTION work_scraper.website_is_stale(source TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    stale BOOLEAN := FALSE;
    curtime TIMESTAMP := now();
    website_id INTEGER;
BEGIN
    -- selecting website id if its stale
    SELECT id INTO website_id
    FROM work_scraper.sources
    WHERE website = source
        AND (
            -- not being scanned, but been more than rescan_interval since last scan
            (scanning = FALSE AND curtime >= status_updated + rescan_interval)
            -- being scanned, but for too long (assuming scraper crashed)
            OR (scanning = TRUE AND curtime >= status_updated + scanning_time)
        );

    IF website_id IS NULL THEN
        stale := FALSE;
    ELSE
        stale := TRUE;
    END IF;

    RETURN stale;
END;
$$;