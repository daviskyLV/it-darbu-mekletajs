CREATE OR REPLACE PROCEDURE work_scraper.delete_unscanned_vacancies(
    vacancy_id INTEGER[]
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    DELETE FROM work_scraper.unscanned_vacancies
    WHERE id = ANY(vacancy_id);
END;
$$;