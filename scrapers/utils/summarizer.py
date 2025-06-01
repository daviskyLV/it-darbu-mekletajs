from util_classes import SummarizedDescription

def create_summarized_description(to_summarize: str, keywords_json: dict[str, dict[str, list[str]]]) -> SummarizedDescription:
    """
    Takes in a string of text and finds keywords related to programming languages,
    business software, programming frameworks, technologies and max required experience.
    """
    return SummarizedDescription(
        languages=[],
        frameworks=keyword_summarizer(to_summarize, keywords_json["frameworks"]),
        year_exp=0,
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
    lower = to_summarize.lower()
    matched: list[str] = []
    for k, v in keywords:
        for srch in v:
            if lower.find(srch):
                matched.append(k)
                break
    
    return matched

def vacancy_valid(summarized: SummarizedDescription | None) -> bool:
    """
    Checks whether vacancy summary is valid enough for the vacancy to be considered relevant.
    """
    if not summarized:
        return False

    if len(summarized.business_software) > 0:
        return True
    if len(summarized.frameworks) > 0:
        return True
    if len(summarized.programming_languages) > 0:
        return True
    if len(summarized.technologies) > 0:
        return True
    if len(summarized.general_keywords) > 0:
        return True

    return False