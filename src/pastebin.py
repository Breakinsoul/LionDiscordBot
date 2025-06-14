import base64
import re
import zlib
import lxml.etree as ET
import aiohttp
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

PASTEBIN_REGEX = re.compile(r"pastebin.com/(\S*)")

def fetch_paste_key(content: str) -> list:
    return re.findall(r'[^raw/]+', content)

def decode_to_xml(enc: str) -> Optional[bytes]:
    try:
        decoded_data = base64.urlsafe_b64decode(enc.replace("-", "+").replace("_", "/"))
        return zlib.decompress(decoded_data)
    except (base64.binascii.Error, zlib.error) as e:
        logger.error(f"Error decoding data: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during decoding: {e}")
        return None

async def get_raw_data_async(url: str) -> Optional[str]:
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.error(f"HTTP {response.status} when fetching {url}")
                    return None
                    
    except aiohttp.ClientError as e:
        logger.error(f"Network error fetching {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return None

def get_raw_data(url: str) -> Optional[str]:
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(get_raw_data_async(url))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(get_raw_data_async(url))
        finally:
            loop.close()

def validate_pastebin_url(paste_key: str) -> bool:
    return paste_key and "pastebin.com" in paste_key

def get_as_xml(paste_key: str) -> Optional[str]:
    try:
        if not validate_pastebin_url(paste_key):
            logger.error(f"Invalid pastebin URL: {paste_key}")
            return None
            
        raw_url = paste_key.replace("pastebin.com", "pastebin.com/raw")
        
        data = get_raw_data(raw_url)
        if not data:
            logger.error("Failed to fetch pastebin data")
            return None
            
        xml_data = decode_to_xml(data)
        if not xml_data:
            logger.error("Failed to decode pastebin data to XML")
            return None
            
        try:
            root = ET.fromstring(xml_data)
            tree = ET.ElementTree(root)
            tree.write("file.xml", encoding="utf-8", xml_declaration=True)
            return xml_data.decode('utf-8')
        except ET.XMLSyntaxError as e:
            logger.error(f"Invalid XML in pastebin data: {e}")
            return None
            
    except Exception as e:
        logger.error(f"Error processing pastebin {paste_key}: {e}")
        return None