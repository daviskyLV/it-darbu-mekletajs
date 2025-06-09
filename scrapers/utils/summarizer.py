from utils.util_classes import SummarizedDescription
from utils.parser import clean_description
import re

def create_summarized_description(to_summarize: str, keywords_json: dict[str, dict[str, list[str]]]) -> SummarizedDescription:
    """
    Takes in a string of text and finds keywords related to programming languages,
    business software, programming frameworks, technologies and max required experience.
    """
    to_summarize = clean_description(to_summarize)
    return SummarizedDescription(
        languages=[],
        frameworks=keyword_summarizer(to_summarize, keywords_json["frameworks"]),
        year_exp=experience_summarizer(to_summarize),
        technologies=keyword_summarizer(to_summarize, keywords_json["technologies"]),
        programming_languages=keyword_summarizer(to_summarize, keywords_json["programmingLanguages"]),
        business_software=keyword_summarizer(to_summarize, keywords_json["businessSoftware"]),
        general_keywords=keyword_summarizer(to_summarize, keywords_json["general"])
    )

def keyword_summarizer(to_summarize: str, keywords: dict[str, list[str]]) -> list[str]:
    """
    Takes in a dictionary of keywords (key) and list of strings that the keyword matches (value),
    and the text to search in for keywords.\n
    Returns: a list of matched keywords (keys)
    """
    to_summarize = to_summarize.lower()
    matched: list[str] = []
    for k in keywords:
        for srch in keywords[k]:
            if to_summarize.find(f" {srch}") >= 0:
                matched.append(k)
                break
    
    return matched

def experience_summarizer(to_summarize: str) -> float:
    """
    Summarizes the max required experience in years from a job description.
    """
    to_summarize = to_summarize.lower()
    # Regex with capture group for the number
    pattern_en = r'\b(\d+)\+?\s+years?\b' # 2+ year(s)/1 year/...
    pattern_lv = r'\b(\d+)\+?\s+gad\b' # 2+ gad(u)/3 gad(iem)/...
    years = [float(match) for match in re.findall(pattern_en, to_summarize)]
    years += [float(match) for match in re.findall(pattern_lv, to_summarize)]
    years.sort()
    
    if len(years) == 0:
        return 0
    else:
        return years[-1]

def vacancy_valid(summarized: SummarizedDescription | None) -> bool:
    """
    Checks whether vacancy summary is valid enough for the vacancy to be considered relevant.
    """
    if not summarized:
        return False
    if len(summarized.general_keywords) == 0:
        # Vacancy must have at least a general keyword to be valid
        return False

    if len(summarized.business_software) > 0:
        return True
    if len(summarized.frameworks) > 0:
        return True
    if len(summarized.programming_languages) > 0:
        return True
    if len(summarized.technologies) > 0:
        return True

    return False