from PIL import Image
import pytesseract
from bs4 import BeautifulSoup

def parse_image_file_to_string(filepath: str, lv_enabled: bool = True, en_enabled: bool = True) -> str:
    """
    Parses a given image from file into text. Can adjust whether to parse in Latvian and/or English. If none enabled, defaults to both.
    """
    if not lv_enabled and not en_enabled:
        lv_enabled = True
        en_enabled = True

    img = Image.open(filepath)
    text = pytesseract.image_to_string(img, lang=f"{"eng" if en_enabled else ""}+{"lav" if lv_enabled else ""}")
    return text

def remove_html_tags(text: str) -> str:
    return BeautifulSoup(text, "lxml").text