import pytesseract
from PIL import Image
from geopy.geocoders import Nominatim


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


def get_address(latitude: float, longitude: float) -> str:
    geolocator = Nominatim(user_agent="test")
    location = geolocator.reverse((latitude, longitude), language="ja")
    return location.address


def get_address_from_image(image_path: str) -> str:
    text = extract_text_from_image(image_path)
    address = get_address(*extract_coordinates(text))
    print("Address:", address)
    return address

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
# print("Address:", address)
