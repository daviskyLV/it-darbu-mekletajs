import psycopg2 as pg
import psycopg2.extensions as pgext
from psycopg2.extras import Json
from dataclasses import asdict
import os, ast
from utils.util_classes import Vacancy, VacanciesList

def get_connection() -> pgext.connection:
    """
    Create a connection to the database. Throws an exception if fails.
    """
    # Connect to the database
    c = pg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "work_scraper"),
        user=os.getenv("DB_SCRAPER_USER", "postgres"),
        password=os.getenv("DB_SCRAPER_PASSWORD", "postgres"),
        port=os.getenv("DB_PORT", 5432)
    )
    return c

def close_connection(conn: pgext.connection):
    """
    Closes the database connection
    """
    conn.close()

def check_if_website_stale(conn: pgext.connection, website: str) -> bool:
    """
    Checks whether the website vacancy list is stale and should be refetched.
    """
    cur: pgext.cursor = conn.cursor()
    cur.execute("SELECT work_scraper.website_is_stale(%s::TEXT);", (website,))
    results = cur.fetchall()
    stale: bool = False
    for r in results:
        stale = bool(r[0])
    cur.close()

    return stale

def set_website_scan_status(conn: pgext.connection, website: str,
                            scanning: bool):
    """
    Sets the website's vacancy scanning status.
    """
    cur: pgext.cursor = conn.cursor()
    cur.execute("CALL work_scraper.mark_website_scanning(%s, %s);", (website, scanning,))
    conn.commit()
    cur.close()

def convert_vacancies_to_columns(vacancies: list[Vacancy]) -> VacanciesList:
    """
    Converts Vacancies list to a columns in following format:\n
    db_id, title, employer, salary_min, salary_max, hourly_rate, remote,
    published, expires, country_code, city_name, fully_fetched, web_id,
    description, summarized_description
    """
    vl: VacanciesList = VacanciesList()

    for v in vacancies:
        vl.db_id.append(v.db_id)
        vl.title.append(v.title)
        vl.employer.append(v.employer)
        vl.salary_min.append(v.salary_min)
        vl.salary_max.append(v.salary_max)
        vl.hourly_rate.append(v.hourly_rate)
        vl.remote.append(v.remote)
        vl.published.append(v.published)
        vl.expires.append(v.expires)
        vl.country_code.append(v.country_code)
        vl.city_name.append(v.city_name)
        vl.web_id.append(v.web_id)
        vl.description.append(v.description)
        vl.summarized_description.append(Json(asdict(v.summarized_description)) if v.summarized_description else None)

    return vl

def add_new_vacancies(conn: pgext.connection, website: str,
                      vacancies: list[Vacancy]):
    """
    Adds up to 1000 new vacancies to the saved vacancy list.
    Optionally, autocloses the database connection.
    """
    if len(vacancies) == 0:
        return

    vac_list = convert_vacancies_to_columns(vacancies)
    cur: pgext.cursor = conn.cursor()
    cur.execute(
        """CALL work_scraper.add_vacancies(
        %s::TEXT[], %s::TEXT[],
        %s::DOUBLE PRECISION[], %s::DOUBLE PRECISION[],
        %s::BOOLEAN[], %s::BOOLEAN[],
        %s::TIMESTAMP[], %s::TIMESTAMP[],
        %s::TEXT[], %s::TEXT[],
        %s::TEXT[], %s::TEXT,
        %s::TEXT[], %s::JSONB[]);""",
        (
            vac_list.title, # title
            vac_list.employer, # employer
            vac_list.salary_min, # salary_min
            vac_list.salary_max, # salary_max
            vac_list.hourly_rate, # hourly_rate
            vac_list.remote, # remote
            vac_list.published, # published
            vac_list.expires, # expires
            vac_list.country_code, # country_code
            vac_list.city_name, # city_name
            vac_list.web_id, # web_id
            website,
            vac_list.description, # description
            vac_list.summarized_description, # summarized_description
        ))
    conn.commit()
    cur.close()

def update_vacancies(conn: pgext.connection, vacancies: list[Vacancy]):
    """
    Updates already existing vacancies in the database.
    """
    if len(vacancies) == 0:
        return
    
    vac_list = convert_vacancies_to_columns(vacancies)
    cur: pgext.cursor = conn.cursor()
    cur.execute(
        """CALL work_scraper.update_vacancies(
        %s::INTEGER[], %s::TEXT[],
        %s::TEXT[], %s::DOUBLE PRECISION[],
        %s::DOUBLE PRECISION[], %s::BOOLEAN[],
        %s::BOOLEAN[], %s::TIMESTAMP[],
        %s::TIMESTAMP[], %s::VARCHAR[],
        %s::TEXT[], %s::TEXT[], %s::JSONB[]);""",
        (
            vac_list.db_id, # db_id
            vac_list.title, # title
            vac_list.employer, # employer
            vac_list.salary_min, # salary_min
            vac_list.salary_max, # salary_max
            vac_list.hourly_rate, # hourly_rate
            vac_list.remote, # remote
            vac_list.published, # published
            vac_list.expires, # expires
            vac_list.country_code, # country_code
            vac_list.city_name, # city_name
            vac_list.description, # description
            vac_list.summarized_description, # summarized_description
        ))
    conn.commit()
    cur.close()

def get_stale_vacancies(conn: pgext.connection, website: str) -> list[tuple[str, int]]:
    """
    Returns up to 20 vacancy web ids and vacancy database ids that are stale for the given source.
    The vacancies are reserved for fetching for 2 hours.\n
    Returns: [(vacancy_web_id, db_row_id)]
    """
    cur: pgext.cursor = conn.cursor()
    cur.execute(
        "SELECT work_scraper.get_stale_vacancies(%s::TEXT);",
        (website,)
    )
    conn.commit()
    results = cur.fetchall()
    
    final: list[tuple[str, int]] = []
    for r in results:
        t = ast.literal_eval(str(r[0]))
        final.append((str(t[0]), int(t[1])))
    cur.close()

    return final

def delete_vacancies(conn: pgext.connection, db_ids: list[int]):
    """
    Deletes specified vacancies from the database.
    """
    if len(db_ids) == 0:
        return

    cur = conn.cursor()
    cur.execute("CALL work_scraper.delete_vacancies(%s::INTEGER[]);", (db_ids,))
    conn.commit()
    cur.close()

def delete_unscanned_vacancies(conn: pgext.connection, db_ids: list[int]):
    """
    Deletes specified unscanned vacancies from the unscanned vacancy table in database.
    """
    if len(db_ids) == 0:
        return

    cur = conn.cursor()
    cur.execute("CALL work_scraper.delete_unscanned_vacancies(%s::INTEGER[]);", (db_ids,))
    conn.commit()
    cur.close()

def add_unscanned_vacancies(conn: pgext.connection, web_ids: list[str], source: str):
    """
    Adds vacancy ids to a list in the database to later fully index them
    """
    if len(web_ids) == 0:
        return

    cur = conn.cursor()
    cur.execute("CALL work_scraper.add_unscanned_vacancies(%s::TEXT[], %s::TEXT);", (web_ids, source))
    conn.commit()
    cur.close()

def get_unscanned_vacancies(conn: pgext.connection, website: str) -> list[tuple[str, int]]:
    """
    Returns up to 20 vacancy web ids and vacancy database ids that haven't been scanned for the given source.
    The vacancies are reserved for fetching for 2 hours. After fetching their info, add them to database by
    using add_new_vacancies() function.\n
    Returns: [(vacancy_web_id, db_row_id)]
    """
    cur: pgext.cursor = conn.cursor()
    cur.execute(
        "SELECT work_scraper.get_unscanned_vacancies(%s::TEXT);",
        (website,)
    )
    conn.commit()
    results = cur.fetchall()
    
    final: list[tuple[str, int]] = []
    for r in results:
        t = ast.literal_eval(str(r[0]))
        final.append((str(t[0]), int(t[1])))
    cur.close()

    return final