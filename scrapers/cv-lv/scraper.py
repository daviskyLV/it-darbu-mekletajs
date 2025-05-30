import requests
import datetime as dt

class Vacancy:
    id: int
    title: str
    employer: str
    salaryMin: int
    salaryMax: int
    hourlyRate: bool
    remote: bool
    published: dt.datetime
    expires: dt.datetime
    countryCode: str
    city: str


def get_locations() -> dict[str, dict[int, str]]:
    """
    Returns cv.lv location data for both countries and towns.
    Structure: {"countries": {countryId: countryName, ...}, "towns": {townId: townName, ...}}
    """
    final: dict[str, dict[int, str]] = {"countries": {}, "towns": {}}
    locations_req = requests.get("https://cv.lv/api/v1/locations-service/list")
    if not locations_req.ok:
        raise Exception(f"Couldn't get location data! Error code: {locations_req.status_code}")
    
    loc_json = locations_req.json()
    for _, country in loc_json["countries"]:
        final["countries"][country.id] = country.iso
    for _, town in loc_json["towns"]:
        final["towns"][town.id] = town.name

    return final

def get_vacancies() -> list[Vacancy]:
    # simple get request of 10000 listings is enough to get all of them
    vacancies_req = requests.get("https://cv.lv/api/v1/vacancy-search-service/search?limit=10000&offset=0&fuzzy=true&showHidden=true")


if __name__ == "__main__":
    locations = get_locations()