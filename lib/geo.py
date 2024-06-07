import pytesseract
from PIL import Image
from geopy.geocoders import Nominatim
from loguru import logger


def extract_text_from_image(image_path: str) -> str:
    return pytesseract.image_to_string(Image.open(image_path))


def extract_coordinates(text: str) -> tuple[float, float] or None:
    lines = text.split("\n")
    for line in lines:
        if line.startswith("N:") and "E:" in line:
            parts = line.split()
            latitude = float(parts[0][2:])
            longitude = float(parts[1][2:])
            return latitude, longitude
    return None, None


def get_address(latitude: float, longitude: float) -> str | None:
    geolocator = Nominatim(user_agent="test")
    location = geolocator.reverse((latitude, longitude), language="ja")
    if location is None or location.address is None:
        return None

    return location.address


def get_address_from_image(image_path: str) -> str | None:
    text = extract_text_from_image(image_path)
    logger.debug(f"OCR Text: {text}")
    address = get_address(*extract_coordinates(text))
    logger.info(f"Address: {address}")
    if address is None:
        return None

    address = str.replace(address, " ", "")
    address_arr = address.split(",")
    if len(address_arr) < 4:
        return None

    pref = address_arr[-3]
    city = address_arr[-4]
    detail = address_arr[0]
    res = f"{pref} {city} {detail}"
    logger.info(f"Custom Address: {res}")
    return res


# def get_address(latitude: float, longitude: float):
#     geolocator = Nominatim(user_agent="test")
#     location = geolocator.reverse((latitude, longitude), language="ja")
#     return location.address
#
#
# latitude = 35.520930
# longitude = 139.693580
#
# address = get_address(latitude, longitude)
# logger.info("Address:", address)
