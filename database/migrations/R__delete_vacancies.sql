CREATE OR REPLACE PROCEDURE work_scraper.delete_vacancies(
    vacancy_id INTEGER[]
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    DELETE FROM work_scraper.vacancies
    WHERE id = ANY(vacancy_id);
END;
$$;