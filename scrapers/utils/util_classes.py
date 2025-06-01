import datetime as dt
from dataclasses import dataclass

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
    fully_fetched: bool
    web_id: str
    description: str | None
    summarized_description: SummarizedDescription | None