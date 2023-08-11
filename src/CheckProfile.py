import requests
import discord

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
def check_profile(nickname, username, member):
    url = f'https://www.pathofexile.com/character-window/get-characters?accountName={username}'
    response = requests.get(url, headers=headers)
    embed = discord.Embed(title=f'\nПроверка профиля {nickname}\nДата создания: {member.created_at.strftime("%d/%m/%Y")}, Присоеденился: {member.joined_at.strftime("%d/%m/%Y")}', description=f'https://ru.pathofexile.com/account/view-profile/{username}', color=0xff4d00)
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/0/08/Path_of_Exile_Logo.png")

    if response.status_code != 200:
        embed.insert_field_at(0, name='\u200b', value='Не удалось получить данные о персонажах либо не верный никнейм должен быть ИмяАккаунтаВПое_РеальноеИмя', inline=False)
    else:
        characters = response.json()
        if len(characters) == 0:
            embed.insert_field_at(0, name='\u200b', value='Указанный пользователь не имеет персонажей', inline=False)
        else:
            embed.insert_field_at(0, name='\u200b', value='Персонажи пользователя:', inline=False)
            for i, character in enumerate(characters, start=1):
                embed.add_field(name=f'{i}) {character["name"]}', value=f'уровень {character["level"]}\nкласс {character["class"]}\nлига {character["league"]}', inline=True)
    return embed