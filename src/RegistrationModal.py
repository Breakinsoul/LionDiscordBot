import discord
import json
import constants
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class RegistrationModal(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction) -> None:
        super().__init__(title='Форма регистрации', timeout=300, custom_id='reg_modal')
        self.interaction = interaction
        
    real_name = discord.ui.TextInput(
        label='Ваше реальное имя',
        placeholder='Ваше имя',
        style=discord.TextStyle.short,
        required=True,
        max_length=50
    )
    
    profile = discord.ui.TextInput(
        label='Профиль PoE (аккаунт или ссылка)',
        placeholder='Профиль PoE',
        style=discord.TextStyle.short,
        required=True,
        max_length=200
    )
    
    playing = discord.ui.TextInput(
        label='Сколько вы уже играете в PoE?',
        placeholder='Опыт игры в PoE',
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    online = discord.ui.TextInput(
        label='Средний онлайн в неделю?',
        placeholder='Часов в неделю',
        style=discord.TextStyle.short,
        required=True,
        max_length=50
    )

    async def save_registration_data(
        self, 
        user_id: int, 
        real_name: str, 
        profile_link: str, 
        playing: str, 
        online: str
    ) -> bool:
        try:
            json_file = constants.json_reg_file
            
            if not os.path.exists(json_file):
                with open(json_file, 'w', encoding='utf-8') as file:
                    json.dump([], file, indent=4, ensure_ascii=False)
            
            with open(json_file, 'r+', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = []
                
                user_present = False
                for user in data:
                    if user.get('user') == user_id:
                        if 'conf' not in user:
                            user['conf'] = {}
                        user['conf'].update({
                            'real_name': real_name,
                            'profile_link': profile_link,
                            'playing': playing,
                            'online': online
                        })
                        user_present = True
                        break
                
                if not user_present:
                    new_record = {
                        'user': user_id,
                        'conf': {
                            'real_name': real_name,
                            'profile_link': profile_link,
                            'playing': playing,
                            'online': online
                        }
                    }
                    data.append(new_record)
                
                file.seek(0)
                file.truncate()
                json.dump(data, file, indent=4, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving registration data for user {user_id}: {e}")
            return False

    def get_profile_link(self, member_name: str) -> str:
        if not member_name:
            return ''
            
        member_name = member_name.strip()
        
        if member_name.startswith('https://'):
            return member_name
        else:
            return f'https://pathofexile.com/account/view-profile/{member_name}'

    def get_member_name(self, profile_link: str) -> str:
        if not profile_link:
            return ''
            
        if profile_link.startswith('https://'):
            return profile_link.split('/')[-1]
        return profile_link

    def validate_inputs(self, real_name: str, profile: str, playing: str, online: str) -> Optional[str]:
        if not real_name or len(real_name.strip()) < 2:
            return "Имя должно содержать минимум 2 символа"
            
        if not profile or len(profile.strip()) < 3:
            return "Профиль должен содержать минимум 3 символа"
            
        if not playing or len(playing.strip()) < 1:
            return "Поле 'Сколько играете' не может быть пустым"
            
        if not online or len(online.strip()) < 1:
            return "Поле 'Онлайн в неделю' не может быть пустым"
            
        return None

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            real_name = self.real_name.value.strip()
            profile_input = self.profile.value.strip()
            playing = self.playing.value.strip()
            online = self.online.value.strip()
            
            validation_error = self.validate_inputs(real_name, profile_input, playing, online)
            if validation_error:
                await interaction.response.send_message(
                    f'Ошибка валидации: {validation_error}',
                    ephemeral=True
                )
                return
            
            profile_link = self.get_profile_link(profile_input)
            profile_name = f'{self.get_member_name(profile_input)}_{real_name}'
            
            user = interaction.user.mention
            user_id = interaction.user.id

            officer_role = interaction.guild.get_role(constants.OF_ROLE_ID)
            candidate_role = interaction.guild.get_role(constants.CANDIDATE_ROLE_ID)
            
            if not officer_role or not candidate_role:
                await interaction.response.send_message(
                    'Ошибка: Необходимые роли не найдены на сервере',
                    ephemeral=True
                )
                return

            reg_embed = discord.Embed(
                title='Заявка на регистрацию',
                description='',
                color=discord.Color.green()
            )
            
            reg_embed.add_field(name='Пользователь', value=user, inline=False)
            reg_embed.add_field(name='Реальное имя', value=real_name, inline=False)
            reg_embed.add_field(name='Профиль PoE', value=profile_link, inline=False)
            reg_embed.add_field(name='Сколько играете в PoE?', value=playing, inline=False)
            reg_embed.add_field(name='Средний онлайн в неделю?', value=online, inline=False)
            reg_embed.add_field(
                name='',
                value=f'Дождитесь ответа от {officer_role.mention} либо зайдите в голосовой канал',
                inline=False
            )

            success = await self.save_registration_data(user_id, real_name, profile_link, playing, online)
            if not success:
                await interaction.response.send_message(
                    'Ошибка при сохранении данных регистрации',
                    ephemeral=True
                )
                return

            try:
                await interaction.user.add_roles(candidate_role, reason="Registration submitted")
            except discord.HTTPException as e:
                logger.warning(f"Failed to add candidate role to {user_id}: {e}")

            membership_channel = interaction.guild.get_channel(constants.MEMBERSHIP_REQ_CHANNEL_ID)
            if membership_channel:
                await membership_channel.send(embed=reg_embed)
            else:
                logger.error("Membership request channel not found")

            await interaction.response.send_message(
                'Регистрация прошла успешно!',
                ephemeral=True
            )

            try:
                await interaction.user.edit(nick=profile_name, reason="Registration completed")
            except discord.HTTPException as e:
                logger.warning(f"Failed to change nickname for {user_id}: {e}")

        except Exception as e:
            logger.error(f"Error in registration submission: {e}")
            try:
                await interaction.response.send_message(
                    'Произошла ошибка при обработке регистрации. Попробуйте еще раз.',
                    ephemeral=True
                )
            except discord.HTTPException:
                pass

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        logger.error(f"Modal error for user {interaction.user.id}: {error}")
        try:
            await interaction.response.send_message(
                'Произошла ошибка при обработке формы. Попробуйте еще раз.',
                ephemeral=True
            )
        except discord.HTTPException:
            pass