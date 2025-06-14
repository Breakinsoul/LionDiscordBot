# Path of Exile Discord Bot

Discord bot for Path of Exile communities with comprehensive features including PoB parsing, news monitoring, user registration, and more.

## Features

### Core Functionality
- **PoB (Path of Building) Integration**: Automatic parsing of Pastebin links with detailed build statistics
- **News Monitoring**: Automated RSS feed checking for Path of Exile Russian news
- **User Registration System**: Guild registration with modal forms and role management
- **Profile Checking**: Character validation through PoE API
- **Wiki Search**: Item search with pricing data from poe.ninja
- **Level 100 Detection**: Automatic role assignment for level 100 achievements

### Commands
- `/reg` - User registration for guild membership
- `/checkprofilepoe <member>` - Check a member's PoE characters
- `/pob <link>` - Parse and display Path of Building data
- `/wiki <search_for> <search>` - Search PoE wiki with price data
- `/sync` - Sync bot commands (owner only)

### Automated Features
- RSS news monitoring (every 10 minutes)
- Level 100 role assignment (daily)
- Price data updates from poe.ninja (hourly)

## Installation

### Prerequisites
- Python 3.8+
- Discord bot token
- Required Python packages (see requirements.txt)

### Setup
1. Clone the repository
```bash
git clone <repository-url>
cd poe-discord-bot
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure bot settings in `constants.py`:
```python
DISCORD_TOKEN = "your_bot_token_here"
GUILD_ID = your_guild_id
MAIN_CHANNEL_ID = your_main_channel_id
RU_NEWS_CHANNEL_ID = your_ru_news_channel_id
RULES_CNANNEL_ID = your_rules_channel_id
USER_ROLE_ID = your_user_role_id
MEMBERSHIP_REQ_CHANNEL_ID = your_membership_req_channel_id
OF_ROLE_ID = your_officer_role_id
CANDIDATE_ROLE_ID = your_candidate_role_id
```

4. Create necessary directories:
```bash
mkdir icons
mkdir news
mkdir ninja_data
```

5. Run the bot:
```bash
python main.py
```

## Configuration

### Required Discord Permissions
- Send Messages
- Embed Links
- Attach Files
- Manage Roles
- Create Public Threads
- Manage Threads
- Read Message History

### File Structure
```
├── main.py                 # Main bot file
├── constants.py           # Configuration settings
├── requirements.txt       # Python dependencies
├── registration_data.json # User registration data
├── src/
│   ├── CheckProfile.py    # Profile checking functionality
│   ├── CheckRSS.py        # RSS news monitoring
│   ├── CreateEmbedHeader.py # PoB embed creation
│   ├── CreateMainEmbed.py # Main PoB embed
│   ├── get_lvled.py       # Level 100 detection
│   ├── ninja_prices.py    # Price data management
│   ├── pastebin.py        # Pastebin link processing
│   ├── pob.py             # PoB command handler
│   ├── RegistrationModal.py # Registration form
│   ├── short.py           # URL shortening
│   ├── usersplit.py       # Username parsing
│   └── wiki_search.py     # Wiki search functionality
├── icons/                 # Character class avatars
├── news/                  # Downloaded news images
└── ninja_data/           # Price data cache
```

## API Dependencies

### External APIs
- **Path of Exile API**: Character and profile data
- **poe.ninja**: Item pricing information
- **PoE Wiki**: Item information and search
- **RSS Feed**: Path of Exile Russian news
- **URL Shortener**: Link compression service

### Rate Limiting
The bot implements proper rate limiting for all external APIs to prevent being blocked.

## Features Detail

### PoB Integration
- Automatic detection of Pastebin links in messages
- Complete build analysis including offense, defense, and resistances
- Character class detection with custom avatars
- Skill gem information display
- Passive tree link extraction

### News Monitoring
- Monitors Path of Exile Russian RSS feed
- Creates Discord threads for each news item
- Downloads and attaches relevant images
- Automatically locks threads after creation

### User Registration
- Modal-based registration form
- Profile validation
- Automatic nickname formatting
- Role assignment system
- Registration data persistence

### Wiki Search
- Item search with autocomplete
- Price integration from poe.ninja
- Multiple search modes (all items, unique only)
- User preference settings for league and visibility

### Level 100 Detection
- Daily scanning of registered users
- Automatic role creation for new leagues
- Achievement announcements
- Persistent role management

## Development

### Adding New Features
1. Create new modules in the `src/` directory
2. Import and integrate in `main.py`
3. Update constants if needed
4. Add appropriate error handling

### Error Handling
The bot includes comprehensive error handling and logging throughout all modules.

### Performance Considerations
- Async/await pattern for all I/O operations
- Connection pooling for HTTP requests
- Efficient data caching for price information
- Rate limiting compliance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under standard terms.

## Support

For issues and feature requests, please use the GitHub issue tracker.
