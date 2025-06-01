import psycopg2 as pg
import psycopg2.extensions as pgext
from psycopg2.extras import Json
from dataclasses import asdict
import os
from util_classes import Vacancy
import pandas as pd

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
    stale: bool = False
    cur: pgext.cursor = conn.cursor()
    cur.execute("SELECT work_scraper.website_is_stale(%s);", (website,))
    stale = bool(cur.fetchone())
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

def convert_vacancies_to_pd(vacancies: list[Vacancy]) -> pd.DataFrame:
    """
    Converts Vacancies list to a pandas DataFrame
    """
    return pd.DataFrame([{
        "db_id": v.db_id,
        "title": v.title,
        "employer": v.employer,
        "salary_min": v.salary_min,
        "salary_max": v.salary_max,
        "hourly_rate": v.hourly_rate,
        "remote": v.remote,
        "published": v.published,
        "expires": v.expires,
        "country_code": v.country_code,
        "city_name": v.city_name,
        "fully_fetched": v.fully_fetched,
        "web_id": v.web_id,
        "description": v.description,
        "summary": Json(asdict(v.summarized_description)) if v.summarized_description else None
    } for v in vacancies])

def add_new_vacancies(conn: pgext.connection, website: str,
                      vacancies: list[Vacancy], autoclose: bool = False):
    """
    Adds up to 1000 new vacancies to the saved vacancy list.
    Optionally, autocloses the database connection.
    """
    df = convert_vacancies_to_pd(vacancies)
    cur: pgext.cursor = conn.cursor()
    cur.execute(
        "CALL work_scraper.add_vacancies(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
        (df["title"].tolist(),
         df["employer"].tolist(),
         df["salary_min"].tolist(),
         df["salary_max"].tolist(),
         df["hourly_rate"].tolist(),
         df["remote"].tolist(),
         df["published"].tolist(),
         df["expires"].tolist(),
         df["country_code"].tolist(),
         df["city_name"].tolist(),
         df["fully_fetched"].tolist(),
         df["web_id"].tolist(),
         website,
         df["description"].tolist(),
         df["summarized"].tolist(),
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
    df = convert_vacancies_to_pd(vacancies)
    cur: pgext.cursor = conn.cursor()
    cur.execute(
        "CALL work_scraper.update_vacancies(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
        (df["db_id"].tolist(),
         df["title"].tolist(),
         df["employer"].tolist(),
         df["salary_min"].tolist(),
         df["salary_max"].tolist(),
         df["hourly_rate"].tolist(),
         df["remote"].tolist(),
         df["published"].tolist(),
         df["expires"].tolist(),
         df["country_code"].tolist(),
         df["city_name"].tolist(),
         df["fully_fetched"].tolist(),
         df["description"].tolist(),
         df["summarized"].tolist(),
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
        "SELECT work_scraper.get_stale_vacancies(%s);",
        (website,)
    )
    conn.commit()
    results = cur.fetchall()
    
    final: list[tuple[str, int]] = []
    for r in results:
        final.append((str(r[0]), int(r[1])))
    cur.close()

    if autoclose:
        close_connection(conn)

    return final

def delete_vacancies(conn: pgext.connection, db_ids: list[int], autoclose: bool = False):
    """
    Deletes specified vacancies from the database.
    Optionally, autocloses the database connection.
    """
    cur = conn.cursor()
    cur.execute("CALL work_scraper.delete_vacancies(%s);", (db_ids,))
    conn.commit()
    cur.close()

    if autoclose:
        close_connection(conn)