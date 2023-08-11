
from src.pastebin import get_as_xml
from src.CreateEmbedHeader import create_embed_header, create_avatar_file
from src.CreateMainEmbed import create_main_embed

def pob_command(link):
    import xml.etree.ElementTree as ET
    def extract_stats(root, element_name):
        return {stat.get('stat'): stat.get('value') for stat in root.iter(element_name)}
    root = ET.fromstring(get_as_xml(link))
    
    stats_dict = extract_stats(root, 'PlayerStat')
    #minion_stats_dict = extract_stats(root, 'MinionStat')
    embed_header = create_embed_header(root, stats_dict)
    embed_avatar_file = create_avatar_file(root)
    embed_header.set_thumbnail(url='attachment://image.webp')
    main_embed = create_main_embed(link, root, stats_dict)

    return embed_header, main_embed, embed_avatar_file
    