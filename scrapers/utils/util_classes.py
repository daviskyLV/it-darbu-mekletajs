import datetime as dt
from dataclasses import dataclass, field
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
    web_id: str
    db_id: int | None = None
    title: str | None = None
    employer: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    hourly_rate: bool | None = None
    remote: bool | None = None
    published: dt.datetime | None = None
    expires: dt.datetime | None = None
    country_code: str | None = None
    city_name: str | None = None
    description: str | None = None
    summarized_description: SummarizedDescription | None = None

@dataclass
class VacanciesList:
    db_id: list[int | None] = field(default_factory=list)
    title: list[str | None] = field(default_factory=list)
    employer: list[str | None] = field(default_factory=list)
    salary_min: list[float | None] = field(default_factory=list)
    salary_max: list[float | None] = field(default_factory=list)
    hourly_rate: list[bool | None] = field(default_factory=list)
    remote: list[bool | None] = field(default_factory=list)
    published: list[dt.datetime | None] = field(default_factory=list)
    expires: list[dt.datetime | None] = field(default_factory=list)
    country_code: list[str | None] = field(default_factory=list)
    city_name: list[str | None] = field(default_factory=list)
    web_id: list[str] = field(default_factory=list)
    description: list[str | None] = field(default_factory=list)
    summarized_description: list[Json | None] = field(default_factory=list)