import aiohttp
import re
import constants

from src.ninja_prices import get_ninja_price

async def get_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data
def get_item_header(name, class_name, rarity):
    header_components = []
    if name != 'None':
        header_components.append(f"{name}")
    if class_name != 'None':
        header_components.append(f"{class_name}")
    if rarity not in ['None','Normal']:
        header_components.append(f"{rarity}")

    link = (f'<https://www.poewiki.net/wiki/{name}>').replace(' ', '_')
    link_text = ', '.join(header_components)
    header = (f"- [{link_text}]({link})\n")
    return header          
def get_drop_areas(drop_areas):
    cleaned_areas = re.findall(r'\[\[.*?\|(.*?)\]\]', drop_areas)
    return cleaned_areas
def find_any(data_item):
    name = data_item['title'].get('name', 'None')  
    class_name = data_item['title'].get('class', 'None')
    drop_areas = data_item['title'].get('drop areas html', 'None')
    tags = data_item['title'].get('tags', 'None')
    rarity = data_item['title'].get('rarity', 'None')
    header = get_item_header(name, class_name, rarity)
    price = get_ninja_price(name, class_name, tags, rarity)
    components = ['']
    if drop_areas != 'None':
        areas = get_drop_areas(drop_areas)
        components.append(f" - Areas: {', '.join(areas)}\n")
    if price:
        components.append(price)
    return header + ''.join(components)

def get_items(data, search_for):
    have_more = False
    found_items = []
    for data_item in data['cargoquery']:
        if search_for == 'any':
            item = find_any(data_item)
            if len(''.join(found_items) + item) > 1900:
                have_more = True
                break
        if search_for == 'unique':
            item = find_any(data_item)
            if len(''.join(found_items) + item) > 1900:
                have_more = True
                break
        found_items.append(item)
    if len(found_items) > 0:
        if have_more:
            items_header = f'>>> Wiki Search: Found more then {len(found_items)} items:\n'
        else:
            items_header = f'>>> Wiki Search: Found {len(found_items)} items:\n'
    else:
        items_header = '>>> Wiki Search: No items found.'
    if found_items != []:
        items = ''.join(found_items)
        return (f'{items_header}{items}')
    else: 
        return {items_header}

async def wiki_search(search_for, search):
    if search_for == 'gem':
        api_entry = constants.gem_api_entry
    elif search_for == 'unique':
        api_entry = constants.uniq_api_entry
    else:
        api_entry = constants.any_api_entry
    url = f'{api_entry}{search}%25%22'
    print(url)
    data = await get_json(url)
    items = get_items(data, search_for)
    
    return items