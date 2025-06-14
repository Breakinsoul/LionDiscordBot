import aiohttp
import re
import constants
import urllib.parse
import discord
from src.ninja_prices import get_ninja_price
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

async def get_json(url: str) -> Optional[Dict]:
    print(f"[GET_JSON] Making request to: {url}")
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"[GET_JSON] Successfully got data")
                    return data
                else:
                    print(f"[GET_JSON] HTTP {response.status} when fetching wiki data")
                    logger.warning(f"HTTP {response.status} when fetching wiki data")
                    return None
    except aiohttp.ClientError as e:
        print(f"[GET_JSON] Network error: {e}")
        logger.error(f"Network error fetching wiki data: {e}")
        return None
    except Exception as e:
        print(f"[GET_JSON] Unexpected error: {e}")
        logger.error(f"Unexpected error fetching wiki data: {e}")
        return None

def get_rarity_color(rarity: str) -> int:
    rarity_colors = {
        'Unique': 0xAF6025,      # Orange
        'Rare': 0xFFFF77,        # Yellow  
        'Magic': 0x8888FF,       # Blue
        'Normal': 0xC8C8C8,      # Light gray
        'Currency': 0xAA9E82,    # Currency brown
        'Gem': 0x1BA29B,         # Gem teal
        'Quest': 0x4AE63A,       # Quest green
        'Divination': 0x0EBAFF,  # Divination card blue
    }
    return rarity_colors.get(rarity, 0x99AAB5)  # Default Discord gray

def get_rarity_emoji(rarity: str) -> str:
    rarity_emojis = {
        'Unique': '🟠',
        'Rare': '🟡', 
        'Magic': '🔵',
        'Normal': '⚪',
        'Currency': '💰',
        'Gem': '💎',
        'Quest': '🟢',
        'Divination': '🃏'
    }
    return rarity_emojis.get(rarity, '⚫')

def get_drop_areas(drop_areas: str) -> List[str]:
    try:
        if not drop_areas or drop_areas == 'None':
            return []
        return re.findall(r'\[\[.*?\|(.*?)\]\]', drop_areas)
    except Exception as e:
        logger.error(f"Error parsing drop areas: {e}")
        return []

def format_price_for_embed(price_info: str) -> str:
    """Очищает и форматирует информацию о ценах для embed"""
    print(f"[FORMAT_PRICE] Input: {repr(price_info)}")
    print(f"[FORMAT_PRICE] Input type: {type(price_info)}")
    
    if not price_info:
        print(f"[FORMAT_PRICE] No price info, returning default")
        return "No price data available"
    
    # Убираем лишние символы и префиксы
    cleaned = price_info.strip()
    print(f"[FORMAT_PRICE] After strip: {repr(cleaned)}")
    
    # Убираем префиксы типа "💎 **Price:**" и "💱 **Exchange:**"
    prefixes_to_remove = [
        "💎 **Price:**", 
        "💱 **Exchange:**", 
        "🔥 **Multiple variants found:**",
        " - Price:",
        " - "
    ]
    
    for prefix in prefixes_to_remove:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            print(f"[FORMAT_PRICE] Removed prefix '{prefix}', result: {repr(cleaned)}")
    
    # Убираем переносы строк в конце
    cleaned = cleaned.rstrip('\n')
    print(f"[FORMAT_PRICE] After rstrip: {repr(cleaned)}")
    
    # Если строка пустая после очистки
    if not cleaned:
        print(f"[FORMAT_PRICE] Empty after cleaning, returning default")
        return "No price data available"
    
    print(f"[FORMAT_PRICE] Final result: {repr(cleaned)}")
    return cleaned

def create_item_embed(item_data: Dict, league: str, search_type: str) -> Optional[discord.Embed]:
    print(f"[CREATE_ITEM_EMBED] Called with league='{league}', search_type='{search_type}'")
    
    try:
        title_data = item_data.get('title', {})
        print(f"[CREATE_ITEM_EMBED] Title data: {title_data}")
        
        name = title_data.get('name', 'Unknown Item')
        class_name = title_data.get('class', 'Unknown')
        drop_areas = title_data.get('drop areas html', '')
        tags = title_data.get('tags', '')
        rarity = title_data.get('rarity', 'Normal')
        
        print(f"[CREATE_ITEM_EMBED] Item: name='{name}', class='{class_name}', rarity='{rarity}'")
        
        # Create embed with rarity-based color
        embed = discord.Embed(
            title=f"{get_rarity_emoji(rarity)} {name}",
            color=get_rarity_color(rarity),
            url=f"https://www.poewiki.net/wiki/{name.replace(' ', '_')}"
        )
        print(f"[CREATE_ITEM_EMBED] Created base embed: {type(embed)}")
        
        # Add basic info
        embed.add_field(
            name="📋 Item Info",
            value=f"**Type:** {class_name}\n**Rarity:** {rarity}",
            inline=True
        )
        print(f"[CREATE_ITEM_EMBED] Added basic info field")
        
        # Add drop areas
        areas = get_drop_areas(drop_areas)
        if areas:
            areas_text = ', '.join(areas[:5])
            if len(areas) > 5:
                areas_text += f" *(+{len(areas) - 5} more)*"
            embed.add_field(
                name="📍 Drop Areas",
                value=areas_text,
                inline=False
            )
            print(f"[CREATE_ITEM_EMBED] Added drop areas field")
        
        # Add price info
        try:
            print(f"[CREATE_ITEM_EMBED] Getting price info...")
            price_info = get_ninja_price(name, class_name, tags, rarity, league)
            print(f"[CREATE_ITEM_EMBED] Price info result: {price_info}")
            print(f"[CREATE_ITEM_EMBED] Price info type: {type(price_info)}")
            
            if price_info:
                formatted_price = format_price_for_embed(price_info)
                print(f"[CREATE_ITEM_EMBED] Formatted price: {formatted_price}")
                embed.add_field(
                    name="💰 Current Price",
                    value=formatted_price,
                    inline=False
                )
                print(f"[CREATE_ITEM_EMBED] Added price field")
            else:
                embed.add_field(
                    name="💰 Current Price",
                    value="No price data available",
                    inline=False
                )
                print(f"[CREATE_ITEM_EMBED] Added no price field")
        except Exception as e:
            print(f"[CREATE_ITEM_EMBED] Price error: {e}")
            print(f"[CREATE_ITEM_EMBED] Price error type: {type(e)}")
            import traceback
            print(f"[CREATE_ITEM_EMBED] Price error traceback: {traceback.format_exc()}")
            
            logger.warning(f"Error getting price for {name}: {e}")
            embed.add_field(
                name="💰 Current Price",
                value="Error loading price data",
                inline=False
            )
            print(f"[CREATE_ITEM_EMBED] Added price error field")
        
        # Add footer
        embed.set_footer(
            text=f"League: {league} • poe.ninja data",
            icon_url="https://upload.wikimedia.org/wikipedia/en/0/08/Path_of_Exile_Logo.png"
        )
        print(f"[CREATE_ITEM_EMBED] Added footer")
        
        print(f"[CREATE_ITEM_EMBED] Returning embed: {type(embed)}")
        return embed
        
    except Exception as e:
        print(f"[CREATE_ITEM_EMBED] EXCEPTION: {e}")
        print(f"[CREATE_ITEM_EMBED] Exception type: {type(e)}")
        import traceback
        print(f"[CREATE_ITEM_EMBED] Full traceback: {traceback.format_exc()}")
        
        logger.error(f"Error creating item embed: {e}")
        return None

def create_search_results_embed(items: List[Dict], league: str, search_type: str, search_query: str) -> discord.Embed:
    print(f"[CREATE_RESULTS_EMBED] Called with {len(items)} items, league='{league}', search_type='{search_type}', query='{search_query}'")
    
    try:
        # Determine embed color based on search type
        color = 0x7289DA if search_type == 'Search' else 0xAF6025  # Blue for all, Orange for uniques
        
        embed = discord.Embed(
            title=f"🔍 Wiki Search Results",
            description=f"**Search:** `{search_query}`\n**League:** {league}\n**Type:** {'All Items' if search_type == 'Search' else 'Unique Items Only'}",
            color=color
        )
        print(f"[CREATE_RESULTS_EMBED] Created base embed: {type(embed)}")
        
        if not items:
            embed.add_field(
                name="❌ No Results",
                value="No items found matching your search criteria.",
                inline=False
            )
            print(f"[CREATE_RESULTS_EMBED] Added no results field")
            return embed
        
        # Process items for compact display
        results_text = []
        for i, item_data in enumerate(items[:10], 1):  # Limit to 10 items
            try:
                title_data = item_data.get('title', {})
                name = title_data.get('name', 'Unknown')
                class_name = title_data.get('class', 'Unknown')
                rarity = title_data.get('rarity', 'Normal')
                tags = title_data.get('tags', '')
                
                print(f"[CREATE_RESULTS_EMBED] Processing item {i}: {name}")
                
                emoji = get_rarity_emoji(rarity)
                
                # Get quick price info
                price_summary = ""
                try:
                    price_info = get_ninja_price(name, class_name, tags, rarity, league)
                    print(f"[CREATE_RESULTS_EMBED] Price info for {name}: {price_info}")
                    
                    if price_info:
                        formatted_price = format_price_for_embed(price_info)
                        # Берем только первую строку для компактности
                        price_lines = formatted_price.split('\n')
                        if price_lines:
                            price_summary = price_lines[0].strip()
                            # Убираем лишние пробелы в начале строки
                            if price_summary.startswith('💎'):
                                price_summary = price_summary[2:].strip()
                        print(f"[CREATE_RESULTS_EMBED] Formatted price for {name}: {price_summary}")
                except Exception as e:
                    print(f"[CREATE_RESULTS_EMBED] Price error for {name}: {e}")
                    logger.debug(f"Price error for {name}: {e}")
                    pass
                
                safe_name = name.replace(' ', '_').replace('(', '%28').replace(')', '%29')
                item_line = f"{emoji} **[{name}](https://www.poewiki.net/wiki/{safe_name})** *({class_name})*"
                if price_summary:
                    item_line += f"\n    💰 {price_summary}"
                
                results_text.append(item_line)
                print(f"[CREATE_RESULTS_EMBED] Added item line: {item_line}")
                
            except Exception as e:
                print(f"[CREATE_RESULTS_EMBED] Error processing item {i}: {e}")
                logger.warning(f"Error processing item {i}: {e}")
                continue
        
        if results_text:
            print(f"[CREATE_RESULTS_EMBED] Processing {len(results_text)} result texts")
            # Split into fields if too long
            current_field = ""
            field_count = 1
            
            for item in results_text:
                test_field = current_field + item + "\n\n"
                if len(test_field) > 1024:  # Discord field limit
                    if current_field.strip():  # Only add if there's content
                        embed.add_field(
                            name=f"📦 Results (Part {field_count})" if field_count > 1 else "📦 Results",
                            value=current_field.strip(),
                            inline=False
                        )
                        print(f"[CREATE_RESULTS_EMBED] Added field part {field_count}")
                    current_field = item + "\n\n"
                    field_count += 1
                else:
                    current_field = test_field
            
            # Add remaining items
            if current_field.strip():
                embed.add_field(
                    name=f"📦 Results (Part {field_count})" if field_count > 1 else "📦 Results",
                    value=current_field.strip(),
                    inline=False
                )
                print(f"[CREATE_RESULTS_EMBED] Added final field part {field_count}")
        
        # Add summary
        total_shown = len(results_text)
        total_available = len(items)
        
        if total_available > total_shown:
            embed.add_field(
                name="ℹ️ Note",
                value=f"Showing {total_shown} of {total_available} results. Refine your search for more specific results.",
                inline=False
            )
            print(f"[CREATE_RESULTS_EMBED] Added summary note")
        
        embed.set_footer(
            text=f"Total: {total_available} items • Powered by poe.ninja",
            icon_url="https://upload.wikimedia.org/wikipedia/en/0/08/Path_of_Exile_Logo.png"
        )
        print(f"[CREATE_RESULTS_EMBED] Added footer")
        
        print(f"[CREATE_RESULTS_EMBED] Returning embed: {type(embed)}")
        return embed
        
    except Exception as e:
        print(f"[CREATE_RESULTS_EMBED] EXCEPTION: {e}")
        print(f"[CREATE_RESULTS_EMBED] Exception type: {type(e)}")
        import traceback
        print(f"[CREATE_RESULTS_EMBED] Full traceback: {traceback.format_exc()}")
        
        logger.error(f"Error creating search results embed: {e}")
        error_embed = discord.Embed(
            title="❌ Search Error",
            description="An error occurred while processing search results.",
            color=0xFF0000
        )
        print(f"[CREATE_RESULTS_EMBED] Returning error embed: {type(error_embed)}")
        return error_embed

async def wiki_search(search_for: str, search: str, league: str) -> discord.Embed:
    print(f"[WIKI_SEARCH] Called with search_for='{search_for}', search='{search}', league='{league}'")
    
    try:
        if not search or not search.strip():
            print(f"[WIKI_SEARCH] Empty search query detected")
            error_embed = discord.Embed(
                title="❌ Invalid Search",
                description="Search query cannot be empty.",
                color=0xFF0000
            )
            print(f"[WIKI_SEARCH] Returning empty search error embed: {type(error_embed)}")
            return error_embed
            
        search = search.strip()
        print(f"[WIKI_SEARCH] Cleaned search query: '{search}'")
        
        if search_for == 'OnlyUniques':
            api_entry = constants.uniq_api_entry
            print(f"[WIKI_SEARCH] Using unique items API")
        elif search_for == 'Search':
            api_entry = constants.any_api_entry
            print(f"[WIKI_SEARCH] Using general search API")
        else:
            print(f"[WIKI_SEARCH] Invalid search type: {search_for}")
            error_embed = discord.Embed(
                title="❌ Invalid Search Type",
                description="Invalid search type specified.",
                color=0xFF0000
            )
            print(f"[WIKI_SEARCH] Returning invalid type error embed: {type(error_embed)}")
            return error_embed
        
        text_url = f'{api_entry}{search}%"'
        print(f"[WIKI_SEARCH] Constructed URL: {text_url}")
        
        try:
            url = urllib.parse.quote(text_url, safe=':/?&=')
            print(f"[WIKI_SEARCH] Encoded URL: {url}")
        except Exception as e:
            print(f"[WIKI_SEARCH] URL encoding error: {e}")
            logger.error(f"Error encoding URL: {e}")
            error_embed = discord.Embed(
                title="❌ Search Error",
                description="Error processing search query.",
                color=0xFF0000
            )
            print(f"[WIKI_SEARCH] Returning URL error embed: {type(error_embed)}")
            return error_embed
        
        print(f"[WIKI_SEARCH] Making API request...")
        data = await get_json(url)
        
        if not data:
            print(f"[WIKI_SEARCH] No data received from API")
            error_embed = discord.Embed(
                title="❌ API Error",
                description="Failed to fetch data from wiki API.",
                color=0xFF0000
            )
            print(f"[WIKI_SEARCH] Returning API error embed: {type(error_embed)}")
            return error_embed
        
        cargoquery = data.get('cargoquery', [])
        print(f"[WIKI_SEARCH] Received {len(cargoquery)} results from API")
        
        # If only one result, show detailed embed
        if len(cargoquery) == 1:
            print(f"[WIKI_SEARCH] Single result detected, creating detailed embed")
            single_embed = create_item_embed(cargoquery[0], league, search_for)
            if single_embed:
                print(f"[WIKI_SEARCH] Created single item embed: {type(single_embed)}")
                # ВАЖНО: убеждаемся что возвращаем именно embed
                if isinstance(single_embed, discord.Embed):
                    return single_embed
                else:
                    print(f"[WIKI_SEARCH] ERROR: single_embed is not an Embed! Type: {type(single_embed)}")
            else:
                print(f"[WIKI_SEARCH] Failed to create single item embed, falling back to results")
        
        # Otherwise show search results
        print(f"[WIKI_SEARCH] Multiple results, creating search results embed")
        results_embed = create_search_results_embed(cargoquery, league, search_for, search)
        print(f"[WIKI_SEARCH] Created results embed: {type(results_embed)}")
        
        # ВАЖНО: убеждаемся что возвращаем именно embed
        if isinstance(results_embed, discord.Embed):
            print(f"[WIKI_SEARCH] Returning valid embed")
            return results_embed
        else:
            print(f"[WIKI_SEARCH] ERROR: results_embed is not an Embed! Type: {type(results_embed)}")
            print(f"[WIKI_SEARCH] Content: {results_embed}")
            # Создаем fallback embed
            fallback_embed = discord.Embed(
                title="❌ Internal Error",
                description="Error creating search results display.",
                color=0xFF0000
            )
            return fallback_embed
        
    except Exception as e:
        print(f"[WIKI_SEARCH] EXCEPTION in wiki_search: {e}")
        print(f"[WIKI_SEARCH] Exception type: {type(e)}")
        import traceback
        print(f"[WIKI_SEARCH] Full traceback: {traceback.format_exc()}")
        
        logger.error(f"Error in wiki search: {e}")
        error_embed = discord.Embed(
            title="❌ Search Error",
            description="An error occurred during search.",
            color=0xFF0000
        )
        print(f"[WIKI_SEARCH] Returning exception error embed: {type(error_embed)}")
        return error_embed