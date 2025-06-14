import aiohttp
import discord
from typing import Optional
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

async def check_profile_async(nickname: str, username: str, member: discord.Member) -> discord.Embed:
    url = f'https://www.pathofexile.com/character-window/get-characters?accountName={username}'
    
    embed = discord.Embed(
        title=f'\nПроверка профиля {nickname}\nДата создания: {member.created_at.strftime("%d/%m/%Y")}, Присоединился: {member.joined_at.strftime("%d/%m/%Y")}',
        description=f'https://ru.pathofexile.com/account/view-profile/{username}',
        color=0xff4d00
    )
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/0/08/Path_of_Exile_Logo.png")

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=HEADERS) as response:
                if response.status != 200:
                    embed.insert_field_at(
                        0, 
                        name='\u200b', 
                        value='Не удалось получить данные о персонажах либо неверный никнейм должен быть ИмяАккаунтаВПое_РеальноеИмя', 
                        inline=False
                    )
                    return embed

                characters = await response.json()
                
                if not characters:
                    embed.insert_field_at(
                        0, 
                        name='\u200b', 
                        value='Указанный пользователь не имеет персонажей', 
                        inline=False
                    )
                else:
                    embed.insert_field_at(
                        0, 
                        name='\u200b', 
                        value='Персонажи пользователя:', 
                        inline=False
                    )
                    
                    for i, character in enumerate(characters[:20], start=1):
                        character_name = character.get('name', 'Unknown')
                        character_level = character.get('level', 'Unknown')
                        character_class = character.get('class', 'Unknown')
                        character_league = character.get('league', 'Unknown')
                        
                        embed.add_field(
                            name=f'{i}) {character_name}',
                            value=f'уровень {character_level}\nкласс {character_class}\nлига {character_league}',
                            inline=True
                        )
                        
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error checking profile for {username}: {e}")
        embed.insert_field_at(
            0, 
            name='\u200b', 
            value='Ошибка сети при получении данных персонажей', 
            inline=False
        )
    except Exception as e:
        logger.error(f"Unexpected error checking profile for {username}: {e}")
        embed.insert_field_at(
            0, 
            name='\u200b', 
            value='Произошла неожиданная ошибка при получении данных', 
            inline=False
        )
    
    return embed

def check_profile(nickname: str, username: str, member: discord.Member) -> discord.Embed:
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(check_profile_async(nickname, username, member))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(check_profile_async(nickname, username, member))
        finally:
            loop.close()