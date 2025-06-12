-- returns up to 20 vacancy web ids and row ids that are stale for the given source
CREATE OR REPLACE FUNCTION work_scraper.get_stale_vacancies(
    source TEXT
)
RETURNS TABLE(vacancy_web_id TEXT, db_id INTEGER)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    curtime TIMESTAMP := now();
    source_id INTEGER;
BEGIN
    SELECT work_scraper.get_website_id(source) INTO source_id;

    -- handling invalid source input
    IF NOT FOUND THEN
        RETURN;
    END IF;

    RETURN QUERY
    WITH to_update AS (
        -- getting vacancies to update
        SELECT v.vacancy_web_id, v.id
        FROM work_scraper.vacancies v
        WHERE curtime >= v.last_checked + INTERVAL '5 days'
            AND v.web_source = source_id
            -- ignoring vacancies that are expired more than a day ago
            AND (v.expires IS NULL OR curtime <= v.expires + INTERVAL '24 hours')
        LIMIT 20
        FOR UPDATE SKIP LOCKED -- locking for update
    ),
    updated AS (
        -- reserving their time
        UPDATE work_scraper.vacancies v
        SET last_checked = curtime - INTERVAL '4 days 22 hours' -- reserving for 2 hours
        FROM to_update tu
        WHERE v.id = tu.id
    )
    -- returning vacancy web ids and database ids
    SELECT tu.vacancy_web_id, tu.id
    FROM to_update tu;
END;
$$;