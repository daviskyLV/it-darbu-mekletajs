import requests
from dotenv import load_dotenv
from utils.util_classes import Vacancy
import utils.db_connection as db
import utils.summarizer as summary
import datetime as dt
import time, os, json

DOMAIN: str = "cv.lv"
REQUEST_DELAY: float = 1

def get_vacancies_list(keywords_json: dict[str, dict[str, list[str]]]) -> list[Vacancy]:
    """
    Returns a list of all available vacancies with partially filled info
    """
    # simple get request of 10000 listings is enough to get all of them
    vacancies_req = requests.get("https://cv.lv/api/v1/vacancy-search-service/search?limit=10000&offset=0")
    if not vacancies_req.ok:
        raise Exception(f"Couldn't get vacancies list! Error code: {vacancies_req.status_code}")
    
    vac_json = vacancies_req.json()
    final: list[Vacancy] = []
    for v in vac_json["vacancies"]:
        summed_description: str = ""
        summed_description += f" {v["positionTitle"]} "
        summed_description += f" {v["positionContent"]} "
        if v["keywords"]:
            for keyv in v["keywords"]:
                summed_description += f" {keyv} "
        
        summarized = summary.create_summarized_description(summed_description, keywords_json)
        if not summary.vacancy_valid(summarized):
            # vacancy didnt have any matching keywords, skipping
            continue

        s_min: float = 0
        s_max: float = 0
        if v["salaryFrom"]:
            s_min = float(v["salaryFrom"])
        if v["salaryTo"]:
            s_max = float(v["salaryTo"])
        else:
            s_max = s_min
        final.append(Vacancy(
                db_id=None,
                web_id=str(v["id"]),
                title=str(v["positionTitle"]),
                employer=str(v["employerName"]),
                published=dt.datetime.fromisoformat(str(v["publishDate"])),
                expires=dt.datetime.fromisoformat(str(v["expirationDate"])),
                salary_min=s_min,
                salary_max=s_max,
                hourly_rate=bool(v["hourlySalary"]),
                remote=bool(v["remoteWork"]),
                country_code=None,
                city_name=None,
                fully_fetched=False,
                description=None,
                summarized_description=summarized
            ))

    return final

def get_nextjs_url() -> str:
    """
    Gets the directory used to access vacancy data via
    /_next/data/[url]/lv/vacancy/[vacancyId]/a/a.json?params=[vacancyId] \n
    Returns: [url] part to use within link
    """
    html_req = requests.get("https://cv.lv/lv/search?limit=20&offset=0&fuzzy=true")
    if not html_req.ok:
        raise Exception("Couldn't fetch vacancy search html!")
    
    sanitized = html_req.text.replace("/_next/static/chunks/", "")
    search_start_tag: str = "<script src=\"/_next/static/"
    search_end_tag: str = "/_"
    index_start = sanitized.find(search_start_tag)
    if index_start == -1:
        raise Exception("Couldn't find nextjs url! (start)")
    
    index_end = sanitized.find(search_end_tag, index_start+len(search_start_tag))
    if index_end == -1:
        raise Exception("Couldn't find nextjs url! (end)")
    
    return sanitized[index_start+len(search_start_tag):index_end]
    
def get_vacancy_data(nextjs_url: str, web_id: str, db_id: int,
                     keywords_json: dict[str, dict[str, list[str]]]) -> Vacancy:
    """
    Gets detailed data about a vacancy, throws an exception if couldn't fetch data.\n
    Returns: Vacancy with nearly all data up to date
    """
    vacancy_req = requests.get(f"https://cv.lv/_next/data/{nextjs_url}/lv/vacancy/{web_id}/a/a.json?params={web_id}")
    if not vacancy_req.ok:
        raise Exception(f"Couldn't fetch vacancy data for {web_id} using nextjs url {nextjs_url}")
    
    jsonified = vacancy_req.json()
    vac_json = jsonified["pageProps"]["vacancy"][web_id]
    loc_json = jsonified["pageProps"]["locations"]
    # getting summarized info about the vacancy
    summed_description: str = ""
    summed_description += f" {vac_json["position"]} "
    for v in vac_json["settings"]["keywords"]:
        summed_description += f" {v["value"]} "
    for v in vac_json["skills"]:
        summed_description += f" {v["value"]} "

    base_desc: str = ""
    if not vac_json["details"]["fileDetails"]:
        # vacancy described in text
        if "nativeTranslation" in vac_json:
            # A native translation exists, using that one
            base_desc += f" {vac_json["nativeTranslation"]["content"]} "
        else:
            for d in vac_json["details"]["standardDetails"]:
                if d["content"]:
                    base_desc += f" {d["content"]} "
    else:
        # vacancy is described using an image
        pass
    summed_description += f" {base_desc} "

    summarized = summary.create_summarized_description(summed_description, keywords_json)
    # adding languages
    for v in vac_json["languages"]:
        summarized.languages.append(v["iso"])

    # Creating final vacancy
    cc: str = str(loc_json["countries"][
        str(vac_json["highlights"]["location"]["countryId"])
    ]["iso"])
    city_matches = [t for t in loc_json["towns"] if t["id"] == vac_json["highlights"]["location"]["townId"]]
    city: str | None = str(city_matches[0]["name"]) if len(city_matches) > 0 else None
    s_min: float = 0
    s_max: float = 0
    if vac_json["highlights"]["salaryFrom"]:
        s_min = float(vac_json["highlights"]["salaryFrom"])
    if vac_json["highlights"]["salaryTo"]:
        s_max = float(vac_json["highlights"]["salaryTo"])
    else:
        s_max = s_min

    return Vacancy(
        db_id=db_id,
        title=str(vac_json["position"]),
        employer=str(vac_json["employerName"]),
        salary_min=s_min,
        salary_max=s_max,
        hourly_rate=(vac_json["highlights"]["ratePer"] != "MONTHLY"),
        remote=bool(vac_json["highlights"]["remoteWork"]),
        published=dt.datetime.fromisoformat(str(vac_json["settings"]["dateStart"])),
        expires=dt.datetime.fromisoformat(str(vac_json["settings"]["dateTo"])),
        country_code=cc,
        city_name=city,
        fully_fetched=True,
        web_id=web_id,
        description=base_desc,
        summarized_description=summarized
    )



if __name__ == "__main__":
    # paths
    script_dir = os.path.dirname(__file__) # absolute dir
    keywords_rel = "keywords.json"
    dotenv_rel = ".env"

    # Load environment variables from .env file
    dotenv_abs = os.path.abspath(os.path.join(script_dir, dotenv_rel))
    load_dotenv(dotenv_abs)
    connection = db.get_connection()

    # Reading keywords.json
    keywords_json: dict[str, dict[str, list[str]]] = {}
    with open(os.path.abspath(os.path.join(script_dir, keywords_rel)), "r") as file:
        keywords_json: dict[str, dict[str, list[str]]] = json.load(file)

    # main loop
    while True:
        # updating website vacancy list if its outdated
        website_stale = db.check_if_website_stale(connection, DOMAIN)
        if website_stale:
            print(f"[{dt.datetime.now().isoformat()}] Website stale, rescanning...!")
            db.set_website_scan_status(connection, DOMAIN, True)
            vacancy_list: list[Vacancy] = []
            try:
                vacancy_list = get_vacancies_list(keywords_json)
            except Exception as e:
                print(f"[{dt.datetime.now().isoformat()}] An exception occoured while getting vacancy list!", e)
            
            # Adding vacancies to the database
            try:
                # splitting into chunks of 500 vacancies per insert
                chunks = [
                    vacancy_list[i:i + 500]
                    for i in range(0, len(vacancy_list), 500)
                ]

                # inserting new vacancies into database
                for c in chunks:
                    db.add_new_vacancies(connection, DOMAIN, c)
            except Exception as e:
                print(f"[{dt.datetime.now().isoformat()}] An exception occoured while adding vacancies to database!", e)
            finally:
                db.set_website_scan_status(connection, DOMAIN, False)
            print(f"[{dt.datetime.now().isoformat()}] Website rescanned!")
        
        # getting stale vacancies to update their info
        nextjs_url: str = ""
        try:
            nextjs_url = get_nextjs_url()
        except:
            # failed to get nextjs url
            continue

        # Fetching full info for stale vacancies
        stale_vacancies = db.get_stale_vacancies(connection, DOMAIN)
        print(f"[{dt.datetime.now().isoformat()}] Fetching info about {len(stale_vacancies)} vacancies...")
        fetched: list[Vacancy] = []
        to_delete: list[int] = []
        for sv in stale_vacancies:
            try:
                data = get_vacancy_data(nextjs_url, sv[0], sv[1], keywords_json)
                if not summary.vacancy_valid(data.summarized_description):
                    if data.db_id:
                        to_delete.append(data.db_id)
                    continue

                # All good, can update in database
                fetched.append(data)
            except Exception as e:
                print(f"[{dt.datetime.now().isoformat()}] Failed to get vacancy data for {sv[0]}", e)
            
            time.sleep(REQUEST_DELAY) # delay between requests
        print(f"[{dt.datetime.now().isoformat()}] Vacancy info fetched!")
        # Performing update
        db.update_vacancies(connection, fetched)
        db.delete_vacancies(connection, to_delete)
        time.sleep(REQUEST_DELAY) # delay between requests