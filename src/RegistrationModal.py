import discord
import json
import constants
import os
import constants

class RegistrationModal(discord.ui.Modal):

    async def save_registration_data(self, user_id, real_name: str, profile_link: str, playing: str, online: str) -> bool:
        new_record = {
            'user': user_id,
            'conf': {
                'real_name': real_name,
                'profile_link': profile_link,
                'playing': playing,
                'online': online
            }   
        }
        json_file = constants.json_reg_file
        if not os.path.exists(json_file):
            with open(json_file, 'w') as file:
                json.dump([], file, indent=4)
        
        with open(json_file, 'r') as file:
            data = json.load(file)
        data.append(new_record)
        with open(json_file, 'w') as file:
            json.dump(data, file, indent=4)

    def get_profile_link(self, member_name):
        return member_name if member_name.startswith('https://') else f'https://pathofexile.com/account/view-profile/{member_name}'

    def get_member_name(self, profile_link):
        return profile_link.split('/')[-1] if profile_link.startswith('https://') else profile_link
    
    def __init__(self, message: discord.Message) -> None:
        super().__init__(title='Форма регистрации', timeout=None, custom_id='reg_modal') 
        
    real_name = discord.ui.TextInput(label='Ваше реальное имя', placeholder='Ваше имя', style=discord.TextStyle.short, required=True)
    profile = discord.ui.TextInput(label='Профиль PoE(сам аккаунт или ссылка)', placeholder='Профиль PoE', style=discord.TextStyle.short, required=True)
    playing = discord.ui.TextInput(label='Сколько вы уже играете в PoE?', placeholder='Сколько вы уже играете в PoE?', style=discord.TextStyle.short, required=True)
    online = discord.ui.TextInput(label='Средний онлайн в неделю?', placeholder='Средний онлайн в неделю?', style=discord.TextStyle.short, required=True)
    async def on_submit(self, interaction: discord.Interaction) -> None:
        real_name = self.real_name.value
        profile_link = self.get_profile_link(self.profile.value)
        profile_name = f'{self.get_member_name(self.profile.value)}_{real_name}'
        playing = self.playing.value
        online = self.online.value
        user = interaction.user.mention
        user_id = interaction.user.id

        officer_role = interaction.guild.get_role(constants.OF_ROLE_ID)
        
        reg_embed = discord.Embed(title=f'Заявка на регистрацию', description='', color=discord.Color.green())
        reg_embed .add_field(name='Пользователь', value=user, inline=False)
        reg_embed.add_field(name='Реальное имя', value=real_name, inline=False)
        reg_embed.add_field(name='Профиль PoE', value=profile_link, inline=False)
        reg_embed.add_field(name='Сколько вы уже играете в PoE?', value=playing, inline=False)
        reg_embed.add_field(name='Средний онлайн в неделю?', value=online, inline=False)
        reg_embed.add_field(name='', value=f'Дождись ответа от {officer_role.mention} либо зайди в голосовой канал', inline=False)
        
        candidate_role = interaction.guild.get_role(constants.CANDIDATE_ROLE_ID)
        
        await interaction.user.add_roles(candidate_role)
        await interaction.guild.get_channel(constants.MEMBERSHIP_REQ_CHANNEL_ID).send(embed=reg_embed)
        await self.save_registration_data(user_id, real_name, profile_link, playing, online)
        await interaction.response.send_message('Регистрация прошла успешно', ephemeral=True, delete_after=5)
        try:
            await interaction.user.edit(nick=profile_name)
        except:
            pass