
import discord
import re
import asyncio
import json
import os

from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime

import constants
from src.CheckProfile import check_profile
from src.CheckRSS import check_new_entries
from src.pob import pob_command
from src.get_lvled import AsyncSetRoles
from src.usersplit import username_splitter
from src.RegistrationModal import RegistrationModal
from main_conf import DISCORD_TOKEN



class LionDiscordBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        
    async def setup_hook(self) -> None:
        self.check_new_entries_task.start()
        self.set_level_roles_to_members.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await self.change_presence(status=discord.Status.online, activity=discord.Game(name="Path of Exile"))

    @tasks.loop(seconds=600) 
    async def check_new_entries_task(self):
        channel = self.get_channel(constants.RU_NEWS_CHANNEL_ID)
        await check_new_entries(channel)
    @check_new_entries_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready() 
    @tasks.loop()
    async def set_level_roles_to_members(self):
        time = datetime.now().strftime('%H:%M:%S')
        print ('-------')
        print(f'[{time}] Started set level roles to members...')
        await asyncio.create_task(AsyncSetRoles(self.get_guild(constants.GUILD_ID), constants.USER_ROLE_ID, self.get_channel(constants.MAIN_CHANNEL_ID)))
        time = datetime.now().strftime('%H:%M:%S')
        print(f'[{time}] Finished set level roles to members...')
    @set_level_roles_to_members.before_loop
    async def before_set_level_roles_to_members(self):
        await self.wait_until_ready()

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        pattern = r'https?://pastebin\.com/[^\s/$.?#].[^\s]*'
        match = re.search(pattern, message.content)
        if match:
            await message.channel.typing()
            link = match.group(0)
            embed_header, main_embed, embed_avatar_file = pob_command(link)
            await message.reply(embeds=[embed_header, main_embed], file=embed_avatar_file)

    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        channel = guild.get_channel(constants.MEMBERSHIP_REQ_CHANNEL_ID)
        await guild.system_channel.send(f'Пользователь {member.mention} зашел на сервер')
        await channel.send(f'Привет,{member.mention}, прочитай правила на канале {member.guild.get_channel(constants.RULES_CNANNEL_ID).mention}, оставь заявку в гильдию через команду /reg', delete_after = 600)
    async def on_member_remove(self, member: discord.Member):
        if member.guild.fetch_ban(member.id) is None:
            return
        await member.guild.system_channel.send(f'Пользователь {member.mention} покинул сервер')
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
        await guild.system_channel.send(f'Пользователь {member.mention} был забанен')
    async def on_member_unban(self, guild: discord.Guild, member: discord.Member):
        await guild.system_channel.send(f'Пользователь {member.mention} был разбанен')


LionDiscordBot = LionDiscordBot(intents=discord.Intents.all())

@LionDiscordBot.tree.command(name='reg', description='Регистрация')
@app_commands.guild_only()
async def reg(interaction: discord.Interaction):

    async def user_is_registered(user) -> bool:
        if os.path.exists('registration_data.json'):
            with open('registration_data.json', 'r') as file:
                json_data = json.load(file)
                return any(record['user'] == user for record in json_data)
        else:
            return False
        
    user_id = interaction.user.id
    if await user_is_registered(user_id):
        await interaction.response.send_message('Пользователь уже зарегистрирован', ephemeral=True, delete_after=5)
        return

    modal = RegistrationModal(interaction)
    await interaction.response.send_modal(modal)

@LionDiscordBot.tree.command(name="checkprofilepoe", description="Check Characters on Profile")
@app_commands.guild_only()
async def checkprofilepoe(interaction, member: discord.Member):
    nickname = member.display_name
    username =  username_splitter(nickname)
    if username:
        check_embed = check_profile(nickname=nickname, username=username, member=member)
        await interaction.response.send_message(embed=check_embed)
    else:
        await interaction.response.send_message('Не верный никнейм в дискорде, должен быть ИмяАккаунтаВПое_РеальноеИмя')
        
@LionDiscordBot.tree.command(name="pob", description="Выводит информацию по билду")
@app_commands.guild_only()
@app_commands.describe(link='Вставьте ссылку на pastebin')
async def pob(interaction: discord.Integration, link:str):
    embed_header, main_embed, embed_avatar_file = pob_command(link)
    await interaction.response.send_message(embeds=[embed_header, main_embed], file=embed_avatar_file)

@LionDiscordBot.tree.command(name='sync')
@app_commands.guild_only()
@commands.is_owner()
async def sync(interaction: discord.Interaction):
    guilds = [guild async for guild in LionDiscordBot.fetch_guilds()]
    for guild in guilds:
        LionDiscordBot.tree.copy_global_to(guild=guild)
        await LionDiscordBot.tree.sync(guild=guild)
        print (await LionDiscordBot.tree.fetch_commands(guild=guild))
        print(f"Synced {guild.name}:{guild.id}")
    await interaction.response.send_message("Synced", ephemeral=True)

LionDiscordBot.run(DISCORD_TOKEN)