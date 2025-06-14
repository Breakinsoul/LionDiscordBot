import discord
import re
import asyncio
import json
import os
import aiohttp
import urllib.parse
from typing import List, Optional, Dict, Any
from datetime import datetime

from discord import app_commands
from discord.ext import commands, tasks
from typing import Literal

import constants
from src.CheckProfile import check_profile
from src.CheckRSS import check_new_entries
from src.pob import pob_command
from src.get_lvled import AsyncSetRoles
from src.usersplit import username_splitter
from src.RegistrationModal import RegistrationModal
from src.wiki_search import wiki_search
from src.ninja_prices import download_ninja_prices


class LionDiscordBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self._session: Optional[aiohttp.ClientSession] = None
        
    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
        
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
        await super().close()
        
    async def setup_hook(self) -> None:
        self.check_new_entries_task.start()
        self.set_level_roles_to_members.start()
        self.grab_ninja_jsons.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await self.change_presence(
            status=discord.Status.online, 
            activity=discord.Game(name="Path of Exile")
        )

    @tasks.loop(hours=1)
    async def grab_ninja_jsons(self):
        try:
            leagues = constants.autocomplete_settings_league
            currencyoverviews = ['Currency', 'Fragment']
            itemoverviews = [
                'DivinationCard', 'DeliriumOrb', 'Artifact', 'Oil', 
                'UniqueWeapon', 'UniqueArmour', 'UniqueAccessory', 
                'UniqueFlask', 'UniqueJewel', 'SkillGem', 'Map', 
                'UniqueMap', 'Invitation', 'Scarab', 'Fossil', 
                'Resonator', 'Essence', 'Vial', 'Tattoo', 'Omen'
            ]
            await download_ninja_prices(leagues, currencyoverviews, itemoverviews)
        except Exception as e:
            print(f"Error in grab_ninja_jsons: {e}")
            
    @grab_ninja_jsons.before_loop
    async def before_grab_ninja_jsons(self):
        await self.wait_until_ready()

    @tasks.loop(minutes=10)
    async def check_new_entries_task(self):
        try:
            channel = self.get_channel(constants.RU_NEWS_CHANNEL_ID)
            if channel:
                await check_new_entries(channel)
        except Exception as e:
            print(f"Error in check_new_entries_task: {e}")
            
    @check_new_entries_task.before_loop
    async def before_check_new_entries(self):
        await self.wait_until_ready()
        
    @tasks.loop(hours=24)
    async def set_level_roles_to_members(self):
        try:
            guild = self.get_guild(constants.GUILD_ID)
            channel = self.get_channel(constants.MAIN_CHANNEL_ID)
            if guild and channel:
                await AsyncSetRoles(guild, constants.USER_ROLE_ID, channel)
        except Exception as e:
            print(f"Error in set_level_roles_to_members: {e}")

    @set_level_roles_to_members.before_loop
    async def before_set_level_roles_to_members(self):
        await self.wait_until_ready()

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
            
        pattern = r'https?://pastebin\.com/[^\s/$.?#].[^\s]*'
        match = re.search(pattern, message.content)
        if match:
            try:
                await message.channel.typing()
                link = match.group(0)
                embed_header, main_embed, embed_avatar_file = pob_command(link)
                await message.reply(embeds=[embed_header, main_embed], file=embed_avatar_file)
            except Exception as e:
                await message.reply(f"Ошибка при обработке PoB ссылки: {e}")

    async def on_member_join(self, member: discord.Member):
        try:
            guild = member.guild
            channel = guild.get_channel(constants.MEMBERSHIP_REQ_CHANNEL_ID)
            rules_channel = guild.get_channel(constants.RULES_CNANNEL_ID)
            
            if guild.system_channel:
                await guild.system_channel.send(f'Пользователь {member.mention} зашел на сервер')
            
            if channel and rules_channel:
                await channel.send(
                    f'Привет, {member.mention}, прочитай правила на канале {rules_channel.mention}, '
                    f'оставь заявку в гильдию через команду /reg',
                    delete_after=600
                )
        except Exception as e:
            print(f"Error in on_member_join: {e}")
            
    async def on_member_remove(self, member: discord.Member):
        try:
            try:
                ban = await member.guild.fetch_ban(member.id)
                if ban:
                    return
            except discord.NotFound:
                pass
            
            if member.guild.system_channel:
                await member.guild.system_channel.send(f'Пользователь {member.mention} покинул сервер')
        except Exception as e:
            print(f"Error in on_member_remove: {e}")
            
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
        try:
            if guild.system_channel:
                await guild.system_channel.send(f'Пользователь {member.mention} был забанен')
        except Exception as e:
            print(f"Error in on_member_ban: {e}")
            
    async def on_member_unban(self, guild: discord.Guild, member: discord.Member):
        try:
            if guild.system_channel:
                await guild.system_channel.send(f'Пользователь {member.mention} был разбанен')
        except Exception as e:
            print(f"Error in on_member_unban: {e}")


def ensure_registration_file():
    if not os.path.exists(constants.json_reg_file):
        with open(constants.json_reg_file, 'w', encoding='utf-8') as file:
            json.dump([], file, indent=4, ensure_ascii=False)


def get_user_registration(user_id: int) -> Optional[Dict[str, Any]]:
    ensure_registration_file()
    try:
        with open(constants.json_reg_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for user in data:
                if user['user'] == user_id:
                    return user
    except (json.JSONDecodeError, FileNotFoundError):
        return None
    return None


def is_user_registered(user_id: int) -> bool:
    user_data = get_user_registration(user_id)
    return (user_data and 
            user_data.get('conf', {}).get('real_name') is not None)


LionDiscordBot = LionDiscordBot(intents=discord.Intents.all())


@LionDiscordBot.tree.command(name='reg', description='Регистрация')
@app_commands.guild_only()
async def reg(interaction: discord.Interaction):
    user_id = interaction.user.id
    if is_user_registered(user_id):
        await interaction.response.send_message(
            'Пользователь уже зарегистрирован', 
            ephemeral=True, 
            delete_after=5
        )
        return

    modal = RegistrationModal(interaction)
    await interaction.response.send_modal(modal)


@LionDiscordBot.tree.command(name="checkprofilepoe", description="Проверить персонажей в профиле")
@app_commands.guild_only()
async def checkprofilepoe(interaction: discord.Interaction, member: discord.Member):
    try:
        nickname = member.display_name
        username = username_splitter(nickname)
        
        if username:
            check_embed = check_profile(nickname=nickname, username=username, member=member)
            await interaction.response.send_message(embed=check_embed)
        else:
            await interaction.response.send_message(
                'Неверный никнейм в Discord, должен быть ИмяАккаунтаВПое_РеальноеИмя',
                ephemeral=True
            )
    except Exception as e:
        await interaction.response.send_message(
            f'Ошибка при проверке профиля: {e}',
            ephemeral=True
        )


@LionDiscordBot.tree.command(name="pob", description="Выводит информацию по билду")
@app_commands.guild_only()
@app_commands.describe(link='Вставьте ссылку на pastebin')
async def pob(interaction: discord.Interaction, link: str):
    try:
        embed_header, main_embed, embed_avatar_file = pob_command(link)
        await interaction.response.send_message(
            embeds=[embed_header, main_embed], 
            file=embed_avatar_file
        )
    except Exception as e:
        await interaction.response.send_message(
            f'Ошибка при обработке PoB ссылки: {e}',
            ephemeral=True
        )


@LionDiscordBot.tree.command(name='sync')
@app_commands.guild_only()
@commands.is_owner()
async def sync(interaction: discord.Interaction):
    try:
        guilds = [guild async for guild in LionDiscordBot.fetch_guilds()]
        for guild in guilds:
            LionDiscordBot.tree.copy_global_to(guild=guild)
            await LionDiscordBot.tree.sync(guild=guild)
        await interaction.response.send_message("Synced", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Sync error: {e}", ephemeral=True)


async def search_autocomplete(
    interaction: discord.Interaction, 
    search: str
) -> List[app_commands.Choice[str]]:
    try:
        search_for = interaction.namespace.search_for
        
        if search_for in ['OnlyUniques', 'Search']:
            api_entry = (constants.uniq_api_entry if search_for == 'OnlyUniques' 
                        else constants.any_api_entry)
            text_url = f'{api_entry}{search}%"'
            url = urllib.parse.quote(text_url, safe=':/?&=')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = [record['title']['name'] for record in data['cargoquery'][:25]]
                        return [app_commands.Choice(name=item, value=item) for item in items]
                        
        elif search_for == 'Setting League':
            leagues = constants.autocomplete_settings_league
            return [app_commands.Choice(name=league, value=league) for league in leagues]
            
        elif search_for == 'Setting Visibility':
            return [
                app_commands.Choice(name=visibility, value=visibility)
                for visibility in ['Public', 'Private']
            ]
    except Exception as e:
        print(f"Error in search_autocomplete: {e}")
    
    return []


def update_user_setting(user_id: int, setting_key: str, setting_value: str):
    ensure_registration_file()
    try:
        with open(constants.json_reg_file, 'r+', encoding='utf-8') as file:
            data = json.load(file)
            user_exists = False
            
            for user in data:
                if user['user'] == user_id:
                    if 'conf' not in user:
                        user['conf'] = {}
                    user['conf'][setting_key] = setting_value
                    user_exists = True
                    break
                    
            if not user_exists:
                new_record = {
                    'user': user_id,
                    'conf': {setting_key: setting_value}
                }
                data.append(new_record)
                
            file.seek(0)
            file.truncate()
            json.dump(data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error updating user setting: {e}")


@LionDiscordBot.tree.command(name="wiki", description="Поиск по wiki")
@app_commands.guild_only()
@app_commands.autocomplete(search=search_autocomplete)
async def wiki(
    interaction: discord.Interaction, 
    search_for: Literal['Search', 'OnlyUniques', 'Setting League', "Setting Visibility"], 
    search: str
):
    print(f"[WIKI] Command called with search_for='{search_for}', search='{search}'")
    
    try:
        if search_for in ['Search', 'OnlyUniques']:
            print(f"[WIKI] Processing search request")
            
            league = constants.default_league
            visibility = constants.default_visibility
            
            user_data = get_user_registration(interaction.user.id)
            if user_data and user_data.get('conf'):
                conf = user_data['conf']
                league = conf.get('league', constants.default_league)
                visibility = conf.get('visibility', constants.default_visibility)
                
            print(f"[WIKI] User settings - league: {league}, visibility: {visibility}")
            
            print(f"[WIKI] Calling wiki_search function...")
            result = await wiki_search(search_for, search, league)
            print(f"[WIKI] wiki_search returned: {type(result)}")
            print(f"[WIKI] Result content preview: {str(result)[:200]}...")
            
            # КРИТИЧЕСКАЯ ПРОВЕРКА: убеждаемся что получили именно Embed
            if not isinstance(result, discord.Embed):
                print(f"[WIKI] CRITICAL ERROR: Result is not an Embed!")
                print(f"[WIKI] Result type: {type(result)}")
                print(f"[WIKI] Result content: {result}")
                
                # Создаем fallback embed из строки
                error_embed = discord.Embed(
                    title="❌ Internal Error", 
                    description="Search function returned invalid format. Please try again.",
                    color=0xFF0000
                )
                
                if visibility == 'Private':
                    await interaction.response.send_message(embed=error_embed, ephemeral=True)
                else:
                    await interaction.response.send_message(embed=error_embed, ephemeral=False)
                return
            
            if hasattr(result, 'to_dict'):
                print(f"[WIKI] Embed has to_dict method - OK")
            else:
                print(f"[WIKI] ERROR: Embed does not have to_dict method!")
                
            if visibility == 'Private':
                print(f"[WIKI] Sending private response")
                await interaction.response.send_message(
                    embed=result, 
                    ephemeral=True
                )
            else:
                print(f"[WIKI] Sending public response")
                await interaction.response.send_message(embed=result, ephemeral=False)
                
        elif search_for == 'Setting League':
            print(f"[WIKI] Updating league setting to: {search}")
            update_user_setting(interaction.user.id, 'league', search)
            success_embed = discord.Embed(
                title="⚙️ Settings Updated",
                description=f'League changed to **{search}**',
                color=0x00FF00
            )
            await interaction.response.send_message(
                embed=success_embed,
                ephemeral=True
            )
            
        elif search_for == "Setting Visibility":
            print(f"[WIKI] Updating visibility setting to: {search}")
            update_user_setting(interaction.user.id, 'visibility', search)
            success_embed = discord.Embed(
                title="⚙️ Settings Updated", 
                description=f'Visibility changed to **{search}**',
                color=0x00FF00
            )
            await interaction.response.send_message(
                embed=success_embed,
                ephemeral=True
            )
    except Exception as e:
        print(f"[WIKI] EXCEPTION in wiki command: {e}")
        print(f"[WIKI] Exception type: {type(e)}")
        import traceback
        print(f"[WIKI] Full traceback: {traceback.format_exc()}")

        error_embed = discord.Embed(
            title="❌ Command Error",
            description=f'An unexpected error occurred: {str(e)[:500]}',
            color=0xFF0000
        )
        try:
            await interaction.response.send_message(
                embed=error_embed, 
                ephemeral=True
            )
        except discord.HTTPException:
            print(f"[WIKI] Failed to send error message")
            pass


if __name__ == "__main__":
    try:
        LionDiscordBot.run(constants.DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot crashed: {e}")
    finally:
        asyncio.run(LionDiscordBot.close())