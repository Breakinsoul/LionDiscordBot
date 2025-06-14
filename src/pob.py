from src.pastebin import get_as_xml
from src.CreateEmbedHeader import create_embed_header, create_avatar_file
from src.CreateMainEmbed import create_main_embed
import xml.etree.ElementTree as ET
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)

def extract_stats(root: ET.Element, element_name: str) -> Dict[str, str]:
    try:
        return {
            stat.get('stat', ''): stat.get('value', '0') 
            for stat in root.iter(element_name) 
            if stat.get('stat') and stat.get('value')
        }
    except Exception as e:
        logger.error(f"Error extracting stats for {element_name}: {e}")
        return {}

def pob_command(link: str) -> Tuple[object, object, object]:
    try:
        xml_data = get_as_xml(link)
        if not xml_data:
            raise ValueError("Failed to get XML data from pastebin link")
            
        root = ET.fromstring(xml_data)
        
        stats_dict = extract_stats(root, 'PlayerStat')
        if not stats_dict:
            logger.warning("No player stats found in PoB data")
            
        embed_header = create_embed_header(root, stats_dict)
        embed_avatar_file = create_avatar_file(root)
        
        if embed_avatar_file:
            embed_header.set_thumbnail(url='attachment://image.webp')
            
        main_embed = create_main_embed(link, root, stats_dict)

        return embed_header, main_embed, embed_avatar_file
        
    except ET.ParseError as e:
        logger.error(f"XML parsing error for link {link}: {e}")
        raise ValueError("Invalid PoB data format")
    except Exception as e:
        logger.error(f"Error processing PoB command for link {link}: {e}")
        raise