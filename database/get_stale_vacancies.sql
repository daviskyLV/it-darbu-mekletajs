-- returns 20 vacancy web ids that are stale for the given source
CREATE OR REPLACE PROCEDURE work_scraper.get_stale_vacancies(source TEXT, OUT vacancy_ids TEXT[])
LANGUAGE plpgsql
AS $$
DECLARE
    curtime TIMESTAMP := now();
    source_id INTEGER;
BEGIN
    SELECT get_website_id(source) INTO source_id;

    -- handling invalid source input
    IF NOT FOUND THEN
        vacancy_ids := ARRAY[]::TEXT[];
        RETURN;
    END IF;

    -- getting vacancies to update
    WITH to_update AS (
        SELECT vacancy_web_id
        FROM work_scraper.vacancies
        WHERE curtime >= last_checked + INTERVAL '5 days' AND web_source = source_id
        LIMIT 20
        FOR UPDATE SKIP LOCKED -- locking for update
    )
    -- updating them
    UPDATE work_scraper.vacancies
    SET last_checked = curtime - INTERVAL '4 days 22 hours' -- reserving for 2 hours
    WHERE web_source = source_id AND vacancy_web_id IN (SELECT vacancy_web_id FROM to_update)
    -- returning back vacancy ids to caller
    RETURNING vacancy_web_id INTO vacancy_ids;
END;
$$;