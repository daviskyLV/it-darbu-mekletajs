from PIL import Image
import pytesseract

def parse_image_file_to_string(filepath: str) -> str:
    img = Image.open(filepath)
    text = pytesseract.image_to_string(img, lang="eng+lav")
    return text