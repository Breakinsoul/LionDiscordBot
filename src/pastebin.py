import base64
import re
import zlib
import lxml.etree as ET
import requests
import re

regex = re.compile(r"pastebin.com/(\S*)")

def fetch_paste_key(content):
    return re.findall(r'[^raw/]+', content)

def decode_to_xml(enc):
    try:
        decoded_data = base64.urlsafe_b64decode(enc.replace("-", "+").replace("_", "/"))
        return zlib.decompress(decoded_data)
    except Exception:
        return None

def get_raw_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        return data
    except requests.exceptions.RequestException as e:
        print(f"Unable to fetch data from {url}: {str(e)}")
        return None

def get_as_xml(paste_key):
    raw_url = paste_key.replace("pastebin.com", "pastebin.com/raw")
    data = get_raw_data(raw_url)
    xml_data = decode_to_xml(data)
    root = ET.fromstring(xml_data)
    tree = ET.ElementTree(root)
    tree.write("file.xml", encoding="utf-8", xml_declaration=True)
    return xml_data.decode()