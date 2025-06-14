import aiohttp
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

API_CONFIG = {
    "url": "https://shorturl9.p.rapidapi.com/functions/api.php",
    "headers": {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": "0892048287msh96453ae8ed0f21fp11c894jsn438e9c6297a4",
        "X-RapidAPI-Host": "shorturl9.p.rapidapi.com"
    }
}

def prepare_link(link: str) -> str:
    if "https://pastebin.com" in link:
        return "pob://pastebin/" + link[18:]
    return link

async def shorten_link_async(link: str) -> str:
    prepared_link = prepare_link(link)
    payload = {"url": prepared_link}
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                API_CONFIG["url"], 
                data=payload, 
                headers=API_CONFIG["headers"]
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success" and data.get("url"):
                        return data["url"]
                else:
                    logger.warning(f"Link shortener API returned status {response.status}")
                    
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error shortening link: {e}")
    except Exception as e:
        logger.error(f"Unexpected error shortening link: {e}")
    
    return link

def link_shortener(link: str) -> str:
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(shorten_link_async(link))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(shorten_link_async(link))
        finally:
            loop.close()