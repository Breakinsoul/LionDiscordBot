from typing import List

DISCORD_TOKEN = "your_bot_token_here" #Discord bot token
GUILD_ID: int = "your_guild_id" #ID of the guild
MAIN_CHANNEL_ID: int = "your_main_channel_id" #ID of the main channel
RU_NEWS_CHANNEL_ID: int = "your_ru_news_channel_id" #ID of the RU news channel
RULES_CNANNEL_ID: int = "your_rules_channel_id" #ID of the rules channel
USER_ROLE_ID: int = "your_user_role_id" #ID of the user role
MEMBERSHIP_REQ_CHANNEL_ID: int = "your_membership_req_channel_id" #ID of the membership request channel
OF_ROLE_ID: int = "your_officer_role_id" #ID of the officer role
CANDIDATE_ROLE_ID: int = "your_candidate_role_id" #ID of the candidate role

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