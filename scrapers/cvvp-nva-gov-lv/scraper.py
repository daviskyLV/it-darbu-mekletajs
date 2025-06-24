import os, json, time
import datetime as dt
import requests
import utils.db_connection as db
from utils.util_funcs import get_random
from utils.util_classes import Vacancy
from utils.parser import remove_html_tags, clean_description
from utils.summarizer import create_summarized_description

DOMAIN: str = "cvvp.nva.gov.lv"

def extract_country_and_city(address: str) -> tuple[str | None, str | None]:
    """
    Returns a tuple of country and city for the address provided.\n
    Returns: [country, city]
    """
    country = None
    city = None
    splitted = address.split(",")
    if len(splitted) > 0:
        country = splitted[0].strip() # Country always first
    if len(splitted) > 2:
        if "LV-" in splitted[2]:
            # A sneaky postal code, city is next
            if len(splitted) > 3:
                city = splitted[3].strip()
        else:
            city = splitted[2].strip()
    
    return (country, city)


def get_vacancies_list(offset: int = 0) -> list[str]:
    """
    Returns a list of all available vacancies (only their ids)
    """
    # GET request to get up to 100 vacancies, 35073957 is IT Technology category
    vacancies_req = requests.get(f"https://cvvp.nva.gov.lv/data/pub_vakance_list?kla_darbibas_joma_id=35073957&limit=100&offset={offset}")
    if not vacancies_req.ok:
        raise Exception(f"Couldn't get vacancies list! Error code: {vacancies_req.status_code}")
    
    vac_json = vacancies_req.json()
    final: list[str] = []
    for v in vac_json:
        final.append(str(v["id"]))

    return final

def get_vacancy_data(vacancy_id: str, db_id: int, keywords_json: dict[str, dict[str, list[str]]]) -> Vacancy:
    """
    Gets detailed data about a vacancy, throws an exception if couldn't fetch data.\n
    Returns: Vacancy with nearly all data up to date
    """
    vacancy_req = requests.get(f"https://cvvp.nva.gov.lv/data/pub_vakance/{vacancy_id}")
    if not vacancy_req.ok:
        raise Exception(f"Couldn't fetch vacancy data for {vacancy_id}")
    
    jsonified = vacancy_req.json()
    summed_desc: str = ""
    summed_desc += f" {jsonified["profesija"]} "
    for v in jsonified["datorprasmes"]:
        summed_desc += f" {v["nosaukums"]} "
    for v in jsonified["esco_prasmes"]:
        summed_desc += f" {v["nosaukums"]} "
    if jsonified["papildus_prasibas"]:
        summed_desc += f" {jsonified["papildus_prasibas"]} "
    
    base_desc: str = str(jsonified["darba_apraksts"])
    try:
        base_desc = remove_html_tags(base_desc)
    except Exception as e:
        print(f"Failed to remove html tags from base description!", e)
    summed_desc += f" {clean_description(base_desc)} "

    languages: list[str] = []
    # adding languages
    for v in jsonified["valodu_zinasanas"]:
        languages.append(v["valoda"])

    summarized = create_summarized_description(summed_desc, keywords_json)
    summarized.languages = languages
    
    country_city = extract_country_and_city(str(jsonified["adrese"]))
    return Vacancy(
        db_id=db_id,
        title=str(jsonified["profesija"]),
        employer=str(jsonified["uznemums"]),
        salary_min=float(str(jsonified["alga_no_lidz"]).split("-")[0]),
        salary_max=float(str(jsonified["alga_no_lidz"]).split("-")[-1]),
        remote=(True if jsonified["ir_attalinati_veicams_darbs"] else False),
        published=dt.datetime.fromisoformat(str(jsonified["publicesanas_datums"])),
        expires=dt.datetime.fromisoformat(str(jsonified["aktuala_lidz"])),
        country_code=country_city[0],
        city_name=country_city[1],
        web_id=vacancy_id,
        description=base_desc.strip(),
        summarized_description=summarized
    )


if __name__ == "__main__":
    # Load environment variables
    web_req_interval = (
        float(os.getenv("WEB_REQUEST_INTERVAL_MIN", "0.5")),
        float(os.getenv("WEB_REQUEST_INTERVAL_MAX", "1.0"))
    )
    db_req_interval = float(os.getenv("DB_REQUEST_INTERVAL", "3.0"))
    nothing_todo_interval = float(os.getenv("NOTHING_TODO_INTERVAL", "60.0"))

    # Reading keywords.json
    keywords_json: dict[str, dict[str, list[str]]] = {}
    with open("/keywords.json", "r") as file:
        keywords_json: dict[str, dict[str, list[str]]] = json.load(file)

    db_con = None
    while True:
        if not db_con:
            db_con = db.get_connection()
        
        # updating website vacancy list if its outdated
        website_stale = db.check_if_website_stale(db_con, DOMAIN)
        if website_stale:
            print(f"[{dt.datetime.now().isoformat()}] Website stale, rescanning...!")
            db.set_website_scan_status(db_con, DOMAIN, True)
            vacancy_list: list[str] = []
            try:
                offset: int = 0
                while True:
                    vacs = get_vacancies_list()
                    vacancy_list = vacancy_list + vacs
                    offset += len(vacs)
                    if len(vacs) < 100:
                        # No more vacancies to iterate through
                        break
                    time.sleep(get_random(web_req_interval[0], web_req_interval[1]))
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
                    db.add_unscanned_vacancies(db_con, c, DOMAIN)
            except Exception as e:
                print(f"[{dt.datetime.now().isoformat()}] An exception occoured while adding unscanned vacancies to database!", e)
            finally:
                db.set_website_scan_status(db_con, DOMAIN, False)
            print(f"[{dt.datetime.now().isoformat()}] Website rescanned!")
            time.sleep(db_req_interval) # letting database rest a little
        
        # Updating unscanned & stale vacancy info
        unscanned_vacancies = db.get_unscanned_vacancies(db_con, DOMAIN)
        if len(unscanned_vacancies) > 0:
            # There are unscanned vacancies to process first
            print(f"[{dt.datetime.now().isoformat()}] Fetching info for {len(unscanned_vacancies)} unscanned vacancies...")
            fetched: list[Vacancy] = []
            for sv in unscanned_vacancies:
                try:
                    data = get_vacancy_data(sv[0], sv[1], keywords_json)
                    fetched.append(data)
                except Exception as e:
                    print(f"[{dt.datetime.now().isoformat()}] Failed to get vacancy data for {sv[0]}", e)
                
                time.sleep(get_random(web_req_interval[0], web_req_interval[1])) # delay between requests
            print(f"[{dt.datetime.now().isoformat()}] Unscanned vacancy info fetched!")
            db.add_new_vacancies(db_con, DOMAIN, fetched)
            ids: list[int] = [i[1] for i in unscanned_vacancies]
            db.delete_unscanned_vacancies(db_con, ids)
            time.sleep(db_req_interval) # letting database rest a little
        
        # getting stale vacancies to update their info
        stale_vacancies = db.get_stale_vacancies(db_con, DOMAIN)
        if len(stale_vacancies) == 0:
            if len(unscanned_vacancies) == 0:
                db.close_connection(db_con)
                db_con = None
                time.sleep(nothing_todo_interval)
            else:
                time.sleep(get_random(web_req_interval[0], web_req_interval[1]))
            continue

        # Fetching full info for stale vacancies
        print(f"[{dt.datetime.now().isoformat()}] Fetching info for {len(stale_vacancies)} stale vacancies...")
        fetched: list[Vacancy] = []
        for sv in stale_vacancies:
            try:
                data = get_vacancy_data(sv[0], sv[1], keywords_json)
                fetched.append(data)
            except Exception as e:
                print(f"[{dt.datetime.now().isoformat()}] Failed to get vacancy data for {sv[0]}", e)
            
            time.sleep(get_random(web_req_interval[0], web_req_interval[1])) # delay between requests
        print(f"[{dt.datetime.now().isoformat()}] Vacancy info fetched!")
        # Performing update
        db.update_vacancies(db_con, fetched)
        time.sleep(db_req_interval) # Letting database rest a little
        time.sleep(get_random(web_req_interval[0], web_req_interval[1]))