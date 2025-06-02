import psycopg2 as pg
import psycopg2.extensions as pgext
from psycopg2.extras import Json
from dataclasses import asdict
import os, ast
from utils.util_classes import Vacancy
import datetime as dt

def get_connection() -> pgext.connection:
    """
    Create a connection to the database. Throws an exception if fails.
    """
    # Database connection details
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))

    # Connect to the database
    c = pg.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return c

def close_connection(conn: pgext.connection):
    """
    Closes the database connection
    """
    conn.close()

def check_if_website_stale(conn: pgext.connection, website: str,
                           autoclose: bool = False) -> bool:
    """
    Checks whether the website vacancy list is stale and should be refetched.
    Optionally, autocloses the database connection.
    """
    cur: pgext.cursor = conn.cursor()
    cur.execute("SELECT work_scraper.website_is_stale(%s::TEXT);", (website,))
    results = cur.fetchall()
    stale: bool = False
    for r in results:
        stale = bool(r[0])
    cur.close()

    if autoclose:
        close_connection(conn)
    return stale

def set_website_scan_status(conn: pgext.connection, website: str,
                            scanning: bool, autoclose: bool = False):
    """
    Sets the website's vacancy scanning status.
    Optionally, autocloses the database connection.
    """
    cur: pgext.cursor = conn.cursor()
    cur.execute("CALL work_scraper.mark_website_scanning(%s, %s);", (website, scanning,))
    conn.commit()
    cur.close()

    if autoclose:
        close_connection(conn)

def convert_vacancies_to_columns(vacancies: list[Vacancy]) -> tuple[
    list[int | None], list[str | None], list[str | None], list[float | None],
    list[float | None], list[bool | None], list[bool | None],
    list[dt.datetime | None], list[dt.datetime | None], list[str | None],
    list[str | None], list[bool], list[str], list[str | None], list[Json | None]
]:
    """
    Converts Vacancies list to a columns in following format:\n
    db_id, title, employer, salary_min, salary_max, hourly_rate, remote,
    published, expires, country_code, city_name, fully_fetched, web_id,
    description, summarized_description
    """
    final: tuple[
        list[int | None], list[str | None], list[str | None], list[float | None],
        list[float | None], list[bool | None], list[bool | None],
        list[dt.datetime | None], list[dt.datetime | None], list[str | None],
        list[str | None], list[bool], list[str], list[str | None], list[Json | None]
    ] = ([], [], [], [], [], [], [], [], [], [], [], [], [], [], [])

    for v in vacancies:
        final[0].append(v.db_id)
        final[1].append(v.title)
        final[2].append(v.employer)
        final[3].append(v.salary_min)
        final[4].append(v.salary_max)
        final[5].append(v.hourly_rate)
        final[6].append(v.remote)
        final[7].append(v.published)
        final[8].append(v.expires)
        final[9].append(v.country_code)
        final[10].append(v.city_name)
        final[11].append(v.fully_fetched)
        final[12].append(v.web_id)
        final[13].append(v.description)
        final[14].append(Json(asdict(v.summarized_description)) if v.summarized_description else None)

    return final

def add_new_vacancies(conn: pgext.connection, website: str,
                      vacancies: list[Vacancy], autoclose: bool = False):
    """
    Adds up to 1000 new vacancies to the saved vacancy list.
    Optionally, autocloses the database connection.
    """
    if len(vacancies) == 0:
        if autoclose:
            close_connection(conn)
        return

    cols = convert_vacancies_to_columns(vacancies)
    cur: pgext.cursor = conn.cursor()
    cur.execute(
        """CALL work_scraper.add_vacancies(
        %s::TEXT[], %s::TEXT[],
        %s::DOUBLE PRECISION[], %s::DOUBLE PRECISION[],
        %s::BOOLEAN[], %s::BOOLEAN[],
        %s::TIMESTAMP[], %s::TIMESTAMP[],
        %s::VARCHAR[], %s::TEXT[],
        %s::BOOLEAN[], %s::TEXT[],
        %s::TEXT, %s::TEXT[], %s::JSONB[]);""",
        (
            cols[1], # title
            cols[2], # employer
            cols[3], # salary_min
            cols[4], # salary_max
            cols[5], # hourly_rate
            cols[6], # remote
            cols[7], # published
            cols[8], # expires
            cols[9], # country_code
            cols[10], # city_name
            cols[11], # fully_fetched
            cols[12], # web_id
            website,
            cols[13], # description
            cols[14], # summarized_description
        ))
    conn.commit()
    cur.close()

    if autoclose:
        close_connection(conn)

def update_vacancies(conn: pgext.connection, vacancies: list[Vacancy],
                     autoclose: bool = False):
    """
    Updates already existing vacancies in the database.
    Optionally, autocloses the database connection.
    """
    if len(vacancies) == 0:
        if autoclose:
            close_connection(conn)
        return
    
    cols = convert_vacancies_to_columns(vacancies)
    cur: pgext.cursor = conn.cursor()
    cur.execute(
        """CALL work_scraper.update_vacancies(
        %s::INTEGER[], %s::TEXT[],
        %s::TEXT[], %s::DOUBLE PRECISION[],
        %s::DOUBLE PRECISION[], %s::BOOLEAN[],
        %s::BOOLEAN[], %s::TIMESTAMP[],
        %s::TIMESTAMP[], %s::VARCHAR[],
        %s::TEXT[], %s::BOOLEAN[],
        %s::TEXT[], %s::JSONB[]);""",
        (
            cols[0], # db_id
            cols[1], # title
            cols[2], # employer
            cols[3], # salary_min
            cols[4], # salary_max
            cols[5], # hourly_rate
            cols[6], # remote
            cols[7], # published
            cols[8], # expires
            cols[9], # country_code
            cols[10], # city_name
            cols[11], # fully_fetched
            cols[13], # description
            cols[14], # summarized_description
        ))
    conn.commit()
    cur.close()

    if autoclose:
        close_connection(conn)

def get_stale_vacancies(conn: pgext.connection, website: str,
                        autoclose: bool = False) -> list[tuple[str, int]]:
    """
    Returns up to 20 vacancy web ids and vacancy database ids that are stale for the given source.
    The vacancies are reserved for fetching for 2 hours.
    Optionally, autocloses the database connection.\n
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

    if autoclose:
        close_connection(conn)

    return final

def delete_vacancies(conn: pgext.connection, db_ids: list[int], autoclose: bool = False):
    """
    Deletes specified vacancies from the database.
    Optionally, autocloses the database connection.
    """
    if len(db_ids) == 0:
        if autoclose:
            close_connection(conn)
        return

    cur = conn.cursor()
    cur.execute("CALL work_scraper.delete_vacancies(%s::INTEGER[]);", (db_ids,))
    conn.commit()
    cur.close()

    if autoclose:
        close_connection(conn)