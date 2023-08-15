
from src.usersplit import username_splitter
import discord
from datetime import datetime
import aiohttp
import asyncio

def get_online_members_count(guild, role_id):
    members_count = 0
    for member in guild.members:
        if member.status != discord.Status.offline:
            for role in member.roles:
                if  role_id == role.id:
                    members_count += 1
    return members_count

async def get_lvled_in_leagues(member: discord.Member, session: aiohttp.ClientSession, sleep_time: int) -> set:
    await asyncio.sleep(sleep_time)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    nickname = member.display_name or member.name
    username_split = username_splitter(nickname) 
    url = f'https://www.pathofexile.com/character-window/get-characters?accountName={username_split}'
    async with session.get(url, headers=headers) as request:
        if request.content_type != 'application/json':
            return None

        response = await request.json()
        if request.status == 200:
            lvled_in_leagues = {character['league'] for character in response if character['level'] == 100}
            return lvled_in_leagues   
        elif request.status == 429:
            repeat_after = int(request.headers.get('Retry-After'))
            print (f'Wait {repeat_after} seconds for next request')
            return await get_lvled_in_leagues(member, session, repeat_after) 
        

async def AsyncSetRoles(guild: discord.guild, role_id: int, channel: discord.channel):
    async with aiohttp.ClientSession() as session:
        for member in guild.members:
            for role in member.roles:
                if role_id == role.id:
                    lvl100leagues = await get_lvled_in_leagues(member=member, session=session, sleep_time=40)
                    if lvl100leagues:
                        for league in lvl100leagues:
                            league_role = discord.utils.get(guild.roles, name=f'{league}: Level 100')
                            message_is_sended = False
                            if league_role is None:
                                league_role = await guild.create_role(name=f'{league}: Level 100', hoist=True, color=0xff5300)
                                message = f'Участник {member.mention} первый поднял уровень 100 на лиге: {league}'
                                await channel.send(message)
                                print (message)
                                message_is_sended = True
                            if league_role not in member.roles: 
                                await member.add_roles(league_role)
                                if message_is_sended == False:
                                    message = f'Участник {member.mention} поднял уровень 100 на лиге: {league}'
                                    #await channel.send(message)
                                    print (message)
    await session.close()