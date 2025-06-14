from src.usersplit import username_splitter
import discord
import aiohttp
import asyncio
from typing import Optional, Set
import logging

logger = logging.getLogger(__name__)

async def get_lvled_in_leagues(
    member: discord.Member, 
    session: aiohttp.ClientSession, 
    sleep_time: int = 40
) -> Optional[Set[str]]:
    try:
        await asyncio.sleep(sleep_time)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        nickname = member.display_name or member.name
        username_split = username_splitter(nickname)
        
        if not username_split:
            logger.warning(f"Could not parse username from {nickname}")
            return None
            
        url = f'https://www.pathofexile.com/character-window/get-characters?accountName={username_split}'
        
        async with session.get(url, headers=headers) as response:
            if response.content_type != 'application/json':
                logger.warning(f"Invalid content type for {username_split}: {response.content_type}")
                return None

            if response.status == 200:
                try:
                    data = await response.json()
                    lvled_in_leagues = {
                        character['league'] 
                        for character in data 
                        if character.get('level') == 100
                    }
                    return lvled_in_leagues
                except Exception as e:
                    logger.error(f"Error parsing JSON for {username_split}: {e}")
                    return None
                    
            elif response.status == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.info(f'Rate limited, waiting {retry_after} seconds for {username_split}')
                return await get_lvled_in_leagues(member, session, retry_after)
                
            else:
                logger.warning(f"HTTP {response.status} for {username_split}")
                return None
                
    except Exception as e:
        logger.error(f"Error getting level 100 data for {member.display_name}: {e}")
        return None


async def AsyncSetRoles(guild: discord.Guild, role_id: int, channel: discord.TextChannel):
    if not guild or not channel:
        logger.error("Guild or channel is None")
        return
        
    target_role = guild.get_role(role_id)
    if not target_role:
        logger.error(f"Role with ID {role_id} not found")
        return
        
    connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = []
        
        for member in guild.members:
            if (target_role in member.roles and 
                member.status != discord.Status.offline and
                not member.bot):
                
                task = process_member(member, session, guild, channel)
                tasks.append(task)
                
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


async def process_member(
    member: discord.Member, 
    session: aiohttp.ClientSession, 
    guild: discord.Guild, 
    channel: discord.TextChannel
):
    try:
        lvl100leagues = await get_lvled_in_leagues(member, session)
        
        if not lvl100leagues:
            return
            
        for league in lvl100leagues:
            await handle_level_100_achievement(member, league, guild, channel)
            
    except Exception as e:
        logger.error(f"Error processing member {member.display_name}: {e}")


async def handle_level_100_achievement(
    member: discord.Member, 
    league: str, 
    guild: discord.Guild, 
    channel: discord.TextChannel
):
    try:
        role_name = f'{league}: Level 100'
        league_role = discord.utils.get(guild.roles, name=role_name)
        
        role_created = False
        if not league_role:
            try:
                league_role = await guild.create_role(
                    name=role_name, 
                    hoist=True, 
                    color=0xff5300,
                    reason=f"Level 100 achievement in {league}"
                )
                role_created = True
                logger.info(f"Created new role: {role_name}")
            except discord.HTTPException as e:
                logger.error(f"Failed to create role {role_name}: {e}")
                return
        
        if league_role not in member.roles:
            try:
                await member.add_roles(league_role, reason=f"Reached level 100 in {league}")
                
                if role_created:
                    message = f'Участник {member.mention} первый поднял уровень 100 на лиге: {league}'
                else:
                    message = f'Участник {member.mention} поднял уровень 100 на лиге: {league}'
                
                await channel.send(message)
                logger.info(f"Added level 100 role to {member.display_name} for league {league}")
                
            except discord.HTTPException as e:
                logger.error(f"Failed to add role to {member.display_name}: {e}")
                
    except Exception as e:
        logger.error(f"Error handling level 100 achievement for {member.display_name}: {e}")