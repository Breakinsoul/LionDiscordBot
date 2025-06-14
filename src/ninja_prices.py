import json
import asyncio
import aiohttp
import aiofiles
import os
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

def safe_get_price_value(item: dict, key: str, default: str = '0') -> str:
    try:
        return str(item.get(key, default))
    except (TypeError, ValueError):
        return default

def format_divine_value(divine_value: float) -> str:
    formatted = "{:.1f}".format(divine_value)
    return formatted.rstrip('0').rstrip('.')

def format_change_percentage(change: float) -> str:
    if change >= 10:
        return f'+{change:.0f}%'
    elif change > 0:
        return f'+{change:.1f}%'
    elif change <= -10:
        return f'{change:.0f}%'
    else:
        return f'{change:.1f}%'

def get_price_from_json_file(file_path: str, name: str) -> Optional[str]:
    try:
        if not os.path.exists(file_path):
            logger.warning(f"Price file not found: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            items = data.get('lines', [])
            
            for item in items:
                if item.get('name') == name:
                    divine_value = float(safe_get_price_value(item, 'divineValue', '0'))
                    chaos_value = int(float(safe_get_price_value(item, 'chaosValue', '0')))
                    formatted_divine_value = format_divine_value(divine_value)
                    
                    sparkline = item.get('sparkline', {})
                    total_change = sparkline.get('totalChange')
                    
                    price_parts = []
                    
                    if chaos_value > 0:
                        price_parts.append(f"💰 {chaos_value:,}c".replace(',', '.'))
                    
                    if divine_value >= 1:
                        price_parts.append(f"✨ {formatted_divine_value}d")
                    
                    if total_change and abs(total_change) > 5:
                        trend_emoji = "📈" if total_change > 0 else "📉"
                        price_parts.append(f"{trend_emoji} {format_change_percentage(total_change)}")
                    
                    if price_parts:
                        return f" 💎 **Price:** {' • '.join(price_parts)}\n"
                    
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.error(f"Error reading price file {file_path}: {e}")
    return None


def get_currency_price_from_json_file(file_path: str, name: str) -> Optional[str]:
    try:
        if not os.path.exists(file_path):
            logger.warning(f"Currency file not found: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            items = data.get('lines', [])
            
            for item in items:
                if item.get('currencyTypeName') == name:
                    receive_data = item.get('receive', {})
                    pay_data = item.get('pay', {})
                    
                    price_parts = []
                    
                    if receive_data:
                        receive_value = int(receive_data.get('value', 0))
                        receive_sparkline = item.get('receiveSparkLine', {})
                        receive_change = receive_sparkline.get('totalChange')
                        
                        receive_text = f"⬇️ {receive_value:,}c".replace(',', '.')
                        if receive_change and abs(receive_change) > 5:
                            trend_emoji = "📈" if receive_change > 0 else "📉"
                            receive_text += f" {trend_emoji} {format_change_percentage(receive_change)}"
                        price_parts.append(receive_text)
                    
                    if pay_data:
                        pay_value = int(1 / pay_data.get('value', 1))
                        pay_sparkline = item.get('paySparkLine', {})
                        pay_change = pay_sparkline.get('totalChange')
                        
                        pay_text = f"⬆️ {pay_value:,}c".replace(',', '.')
                        if pay_change and abs(pay_change) > 5:
                            trend_emoji = "📈" if pay_change > 0 else "📉"
                            pay_text += f" {trend_emoji} {format_change_percentage(pay_change)}"
                        price_parts.append(pay_text)
                    
                    if price_parts:
                        return f" 💱 **Exchange:** {' • '.join(price_parts)}\n"
                        
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.error(f"Error reading currency file {file_path}: {e}")
    return None


def get_uniques_price_from_json_file(file_path: str, name: str, tags: str) -> Optional[str]:
    try:
        if not os.path.exists(file_path):
            logger.warning(f"Uniques file not found: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            items = data.get('lines', [])
            uniques_records = []
            
            for item in items:
                if item.get('name') != name:
                    continue
                    
                chaos_value = int(float(safe_get_price_value(item, 'chaosValue', '0')))
                divine_value = float(safe_get_price_value(item, 'divineValue', '0'))
                formatted_divine_value = format_divine_value(divine_value)
                
                sparkline = item.get('sparkline', {})
                total_change = sparkline.get('totalChange')
                
                links = item.get('links')
                item_class = str(item.get('itemClass', ''))
                variant = item.get('variant')
                map_tier = item.get('mapTier')
                
                variant_parts = []
                price_parts = []
                
                if links and links != 'None':
                    variant_parts.append(f"🔗 {links}L")
                    
                if item_class == "9":
                    variant_parts.append("🏺 Relic")
                    
                if variant and variant != 'None':
                    if "gem,default" in tags:
                        variant_text = f'Level {variant}'
                        if variant.endswith('c'):
                            variant_text = variant_text.replace("c", " corrupted")
                        variant_parts.append(f"💎 {variant_text}")
                    else:
                        variant_parts.append(f"⚡ {variant}")
                        
                if map_tier and map_tier != 'None':
                    variant_parts.append(f"🗺️ T{map_tier}")
                
                if chaos_value > 0:
                    price_parts.append(f"💰 {chaos_value:,}c".replace(',', '.'))
                
                if divine_value >= 0.5:
                    price_parts.append(f"✨ {formatted_divine_value}d")
                    
                if total_change and abs(total_change) > 5:
                    trend_emoji = "📈" if total_change > 0 else "📉"
                    price_parts.append(f"{trend_emoji} {format_change_percentage(total_change)}")
                
                variant_text = f" ({' • '.join(variant_parts)})" if variant_parts else ""
                price_text = ' • '.join(price_parts) if price_parts else "No price data"
                
                uniques_records.append(f"   💎 {price_text}{variant_text}")
            
            if len(uniques_records) > 1:
                header = f" 🔥 **Multiple variants found:**\n"
                return header + '\n'.join(uniques_records) + '\n'
            elif len(uniques_records) == 1:
                return f" 💎 **Price:** {uniques_records[0].strip().replace('💎 ', '')}\n"
                
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.error(f"Error reading uniques file {file_path}: {e}")
    return None


def get_ninja_price(name: str, class_name: str, tags: str, rarity: str, league: str) -> Optional[str]:
    try:
        splited_tags = tags.split(',') if tags else []
        logger.debug(f'Processing: name={name}, class={class_name}, tags={tags}, rarity={rarity}')
        
        json_folder = 'ninja_data'
        artifacts = ['Exotic Coinage', 'Burial Medallion', 'Scrap Metal', 'Astragali']
        accessories_types = ['belt', 'ring', 'amulet']
        
        price_mappings = [
            (lambda: tags == "affliction_orb,currency,default", f'{json_folder}/{league}_DeliriumOrb.json'),
            (lambda: tags == "currency,default" and not any(x in name for x in ["Fossil", "Vial", "Omen", "Tattoo"]), f'{json_folder}/{league}_Currency.json'),
            (lambda: "divination_card,default" in tags, f'{json_folder}/{league}_DivinationCard.json'),
            (lambda: class_name == "Map Fragment" and tags == "default", f'{json_folder}/{league}_Fragment.json'),
            (lambda: name in artifacts, f'{json_folder}/{league}_Artifact.json'),
            (lambda: tags == "mushrune,currency,default", f'{json_folder}/{league}_Oil.json'),
            (lambda: "weapon,default" in tags and rarity == "Unique", f'{json_folder}/{league}_UniqueWeapon.json'),
            (lambda: "armour,default" in tags and rarity == "Unique", f'{json_folder}/{league}_UniqueArmour.json'),
            (lambda: any(tag in accessories_types for tag in splited_tags) and rarity == "Unique", f'{json_folder}/{league}_UniqueAccessory.json'),
            (lambda: "flask,default" in tags and rarity == "Unique", f'{json_folder}/{league}_UniqueFlask.json'),
            (lambda: class_name == "Jewel" and rarity == "Unique", f'{json_folder}/{league}_UniqueJewel.json'),
            (lambda: "gem,default" in tags, f'{json_folder}/{league}_SkillGem.json'),
            (lambda: "map,default" in tags and rarity == "Unique", f'{json_folder}/{league}_UniqueMap.json'),
            (lambda: "primordial_map,default" in tags or "maven_map" in tags, f'{json_folder}/{league}_Invitation.json'),
            (lambda: any(x in tags for x in ["gilded_scarab", "polished_scarab", "jewelled_scarab", "rusted_scarab"]), f'{json_folder}/{league}_Scarab.json'),
            (lambda: tags == "currency,default" and "Fossil" in name, f'{json_folder}/{league}_Fossil.json'),
            (lambda: class_name == "Resonator", f'{json_folder}/{league}_Resonator.json'),
            (lambda: tags == "essence,currency,default", f'{json_folder}/{league}_Essence.json'),
            (lambda: "Vial of" in name, f'{json_folder}/{league}_Vial.json'),
            (lambda: "Tattoo" in name, f'{json_folder}/{league}_Tattoo.json'),
            (lambda: "Omen" in name, f'{json_folder}/{league}_Omen.json'),
        ]
        
        for condition, file_path in price_mappings:
            if condition():
                if "Currency.json" in file_path and tags == "currency,default":
                    return get_currency_price_from_json_file(file_path, name)
                elif any(x in file_path for x in ["Unique", "SkillGem"]):
                    return get_uniques_price_from_json_file(file_path, name, tags)
                else:
                    return get_price_from_json_file(file_path, name)
                    
    except Exception as e:
        logger.error(f"Error getting ninja price for {name}: {e}")
    return None


async def download_ninja_prices(leagues: List[str], currencyoverviews: List[str], itemoverviews: List[str]):
    ninja_json_link_start = 'https://poe.ninja/api/data/'
    os.makedirs('ninja_data', exist_ok=True)
    
    connector = aiohttp.TCPConnector(limit=10, limit_per_host=3)
    timeout = aiohttp.ClientTimeout(total=60)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = []
        
        for league in leagues:
            for currency in currencyoverviews:
                url = f'{ninja_json_link_start}currencyoverview?league={league}&type={currency}'
                filename = f'ninja_data/{league}_{currency}.json'
                tasks.append(download_file(session, url, filename))
                
            for item in itemoverviews:
                url = f'{ninja_json_link_start}itemoverview?league={league}&type={item}'
                filename = f'ninja_data/{league}_{item}.json'
                tasks.append(download_file(session, url, filename))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for result in results if result is True)
        error_count = len(results) - success_count
        
        logger.info(f"Downloaded ninja prices: {success_count} success, {error_count} errors")


async def download_file(session: aiohttp.ClientSession, url: str, filename: str) -> bool:
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.read()
                async with aiofiles.open(filename, 'wb') as f:
                    await f.write(data)
                return True
            else:
                logger.warning(f"Failed to download {url}: HTTP {response.status}")
                return False
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return False