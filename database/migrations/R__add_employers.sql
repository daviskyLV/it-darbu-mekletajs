-- used to add employers, returns employer ids
CREATE OR REPLACE PROCEDURE work_scraper.add_employers(
    employers TEXT[], OUT employer_ids INTEGER[]
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- inserting missing employers
    -- filtering out null values
    WITH filter_nulls AS (
        SELECT DISTINCT e.title
        FROM unnest(employers) AS e(title)
        WHERE e.title IS NOT NULL
    )
    -- inserting non null employers
    INSERT INTO work_scraper.employers (title)
    SELECT title FROM filter_nulls
    ON CONFLICT DO NOTHING;

    -- selecting employer ids from titles, while leaving null values as null
    SELECT ARRAY(
        SELECT e.id
        FROM unnest(employers) WITH ORDINALITY AS input(title, ord) -- to keep correct order
        -- left join to keep nulls
        LEFT JOIN work_scraper.employers e ON e.title = input.title
        ORDER BY ord
    )
    INTO employer_ids;
END;
$$;