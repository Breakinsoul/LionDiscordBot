from typing import List

DISCORD_TOKEN = "your_bot_token_here"
GUILD_ID: int = 989860441176035328
MAIN_CHANNEL_ID: int = 989860441176035331
RU_NEWS_CHANNEL_ID: int = 1383299940981145673
RULES_CNANNEL_ID: int = 989860441176035331
USER_ROLE_ID: int = 463128518562152461
MEMBERSHIP_REQ_CHANNEL_ID: int = 989860441176035331
OF_ROLE_ID: int = 197084204297617408
CANDIDATE_ROLE_ID: int = 1139581517299990658

autocomplete_settings_league: List[str] = [
    'Mercenaries'
]

API_BASE_URL: str = 'https://www.poewiki.net/api.php'
API_PARAMS: str = 'action=cargoquery&tables=items&fields=name,class,drop_areas_html,rarity,tags&group_by=name&format=json'

BASE_FILTERS: str = 'NOT class="Quest Item" AND NOT class="Cosmetic Item" AND NOT class="Hideout Decoration"'

any_api_entry: str = f'{API_BASE_URL}?{API_PARAMS}&where={BASE_FILTERS} AND name LIKE "%'
uniq_api_entry: str = f'{API_BASE_URL}?{API_PARAMS}&where=rarity="Unique" AND {BASE_FILTERS} AND name LIKE "%'

json_reg_file: str = 'registration_data.json'
default_league: str = 'necropolis'
default_visibility: str = 'Public'

TIMEOUT_SETTINGS = {
    'http_request': 15,
    'file_download': 30,
    'api_request': 10
}

RATE_LIMITS = {
    'poe_api_delay': 40,
    'ninja_api_delay': 1,
    'max_concurrent_requests': 10,
    'max_requests_per_host': 5
}

POESESSID = '29f6900981b6a916b50d6a558063d9cd'