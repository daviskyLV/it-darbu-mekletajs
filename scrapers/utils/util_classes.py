import datetime as dt
from dataclasses import dataclass
from psycopg2.extras import Json

@dataclass
class SummarizedDescription:
    languages: list[str]
    frameworks: list[str]
    year_exp: float
    technologies: list[str]
    business_software: list[str]
    programming_languages: list[str]
    general_keywords: list[str]

@dataclass
class Vacancy:
    db_id: int | None
    title: str | None
    employer: str | None
    salary_min: float | None
    salary_max: float | None
    hourly_rate: bool | None
    remote: bool | None
    published: dt.datetime | None
    expires: dt.datetime | None
    country_code: str | None
    city_name: str | None
    web_id: str
    description: str | None
    summarized_description: SummarizedDescription | None

@dataclass
class VacanciesList:
    db_id: list[int | None] = []
    title: list[str | None] = []
    employer: list[str | None] = []
    salary_min: list[float | None] = []
    salary_max: list[float | None] = []
    hourly_rate: list[bool | None] = []
    remote: list[bool | None] = []
    published: list[dt.datetime | None] = []
    expires: list[dt.datetime | None] = []
    country_code: list[str | None] = []
    city_name: list[str | None] = []
    web_id: list[str] = []
    description: list[str | None] = []
    summarized_description: list[Json | None] = []