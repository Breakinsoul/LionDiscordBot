from typing import Optional
import discord
import re
import asyncio
from discord.interactions import Interaction

from discord.utils import MISSING

from src.CheckProfile import check_profile
from src.CheckRSS import check_new_entries
from main_conf import DISCORD_TOKEN
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import check
from discord.ext import tasks
from src.pob import pob_command
from src.get_lvled import AsyncSetRoles
from src.usersplit import username_splitter
from datetime import datetime
import json

CHECK_INTERVAL = 10
GUILD_ID = 188669988012294144
MAIN_CHANNEL = 188669988012294144
RU_NEWS_CHANNEL = 1129727780528078918
OF_ROLE_ID = 197084204297617408
CANDIDATE_ROLE_ID = 1139581517299990658

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

    @tasks.loop(seconds=CHECK_INTERVAL)  # task runs every 60 seconds
    async def check_new_entries_task(self):
        channel = self.get_channel(RU_NEWS_CHANNEL)
        await check_new_entries(channel)
    @check_new_entries_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

    @tasks.loop()
    async def set_level_roles_to_members(self):
        time = datetime.now().strftime('%H:%M:%S')
        print ('-------')
        print(f'[{time}] Started set level roles to members...')
        await asyncio.create_task(AsyncSetRoles(self.get_guild(GUILD_ID), 463128518562152461, self.get_channel(MAIN_CHANNEL)))
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
        channel = guild.get_channel(945664078305693736)
        await guild.system_channel.send(f'Пользователь {member.mention} зашел на сервер')
        await channel.send(f'Привет,{member.mention}, прочитай правила на канале {member.guild.get_channel(945713995606814801).mention}, оставь заявку в гильдию через команду /reg', delete_after = 600)
    async def on_member_remove(self, member: discord.Member):
        if member.guild.fetch_ban(member.id) is None:
            return
        await member.guild.system_channel.send(f'Пользователь {member.mention} покинул сервер')
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
        await guild.system_channel.send(f'Пользователь {member.mention} был забанен')
    async def on_member_unban(self, guild: discord.Guild, member: discord.Member):
        await guild.system_channel.send(f'Пользователь {member.mention} был разбанен')


LionDiscordBot = LionDiscordBot(intents=discord.Intents.all())

async def find_member(user, json_data) -> bool:
    for record in json_data:
        if record['user'] == user:
            return True
    return False
async def save_registration_data(interaction: discord.Interaction,real_name: str, profile_link: str, playing: str, online: str, json_data) -> bool:
    new_record = {'user': interaction.user.id,'real_name': real_name,'profile_link': profile_link,'playing': playing,'online': online}
    json_data.append(new_record)
def get_profile_link(member_name):
    if member_name.startswith('https://'):
        return member_name
    else:
        return f'https://pathofexile.com/account/view-profile/{member_name}'
def get_member_name(profile_link):
    if profile_link.startswith('https://'):
        return profile_link.split('/')[-1]
    else:
        return profile_link

@LionDiscordBot.tree.command(name='reg', description='Регистрация')
@app_commands.guild_only()
async def reg(interaction: discord.Interaction):
    file_name = 'registration_data.json'
    try:
        with open(file_name, 'r') as file:
            json_data = json.load(file)
    except FileNotFoundError:
        json_data = []
    is_member_registerd = await find_member(interaction.user.id, json_data)
    if is_member_registerd:
        await interaction.response.send_message('Пользователь уже зарегистрирован', ephemeral=True, delete_after=5)
        return
    class reg_modal(discord.ui.Modal):
        def __init__(self, message: discord.Message) -> None:
            super().__init__(title='Форма регистрации', timeout=1000, custom_id='reg_modal') 
            
        real_name = discord.ui.TextInput(label='Ваше реальное имя', placeholder='Ваше имя', style=discord.TextStyle.short, required=True)
        profile = discord.ui.TextInput(label='Профиль PoE(сам аккаунт или ссылка)', placeholder='Профиль PoE', style=discord.TextStyle.short, required=True)
        playing = discord.ui.TextInput(label='Сколько вы уже играете в PoE?', placeholder='Сколько вы уже играете в PoE?', style=discord.TextStyle.short, required=True)
        online = discord.ui.TextInput(label='Средний онлайн в неделю?', placeholder='Средний онлайн в неделю?', style=discord.TextStyle.short, required=True)
        async def on_submit(self, interaction: discord.Interaction) -> None:
            real_name = self.real_name.value
            profile_link = get_profile_link(self.profile.value)
            profile_name = f'{get_member_name(profile_link)}_{real_name}'
            playing = self.playing.value
            online = self.online.value
            user = interaction.user.mention
            officer_role = interaction.guild.get_role(OF_ROLE_ID)
            
            await save_registration_data(interaction, real_name, profile_link, playing, online, json_data)
            with open(file_name, 'w') as file:
                    json.dump(json_data, file, indent=4)
            await interaction.response.send_message('Регистрация прошла успешно', ephemeral=True, delete_after=5)
            reg_embed = discord.Embed(title=f'Заявка на регистрацию', description='', color=discord.Color.green())
            reg_embed .add_field(name='Пользователь', value=user, inline=False)
            reg_embed.add_field(name='Реальное имя', value=real_name, inline=False)
            reg_embed.add_field(name='Профиль PoE', value=profile_link, inline=False)
            reg_embed.add_field(name='Сколько вы уже играете в PoE?', value=playing, inline=False)
            reg_embed.add_field(name='Средний онлайн в неделю?', value=online, inline=False)
            reg_embed.add_field(name='', value=f'Дождись ответа от {officer_role.mention} либо зайди в голосовой канал', inline=False)
            candidate_role = interaction.guild.get_role(CANDIDATE_ROLE_ID)
            await interaction.user.edit(nick=profile_name)
            await interaction.user.add_roles(candidate_role)
            await interaction.guild.get_channel(945664078305693736).send(embed=reg_embed)
        
    modal = reg_modal(interaction)
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