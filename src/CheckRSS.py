import discord
import feedparser
import re
import aiohttp
import aiofiles
import os

from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
def convert_links(text):
    pattern = r'<a\s+href="([^"]+)">([^<]+)</a>'
    converted_text = re.sub(pattern, r'[\2](\1)', text)
    return converted_text
async def parse_news_img(link, session):
    async with session.get(link, headers=headers) as response:

        response_text = await response.text()
        if response.status != 200:
            return None
        
        soup = BeautifulSoup(response_text, 'html.parser')

        div_box_content = soup.find('div', class_='box-content s-pad')
        if div_box_content is None:
            return None
        
        img_src = div_box_content.find('img')['src']
        if img_src is None:
            return None

        folder_name = 'news'
        os.makedirs(folder_name, exist_ok=True)
        file_name = img_src.split('/')[-1]
        save_path = os.path.join(folder_name, file_name)

        async with session.get(img_src, headers=headers) as img_response:
            if img_response.status != 200:
                return None
            async with aiofiles.open(save_path, 'wb') as file:
                await file.write(await img_response.read())
                return file_name

async def check_new_entries(channel):
    all_threads = {thread.name for thread in channel.threads}
    
    async for archived_thread in channel.archived_threads():
        all_threads.add(archived_thread.name)

    async with aiohttp.ClientSession() as session:
        async with session.get('https://ru.pathofexile.com/news/rss', headers=headers) as response:
            feed = feedparser.parse(await response.text())
            if response.status != 200:
                print(f'Error in check_new_entries: {response.status} : {response.reason}')
                return
            for entry in feed.entries:
                if entry.title not in all_threads:
                    converted_text = convert_links(entry.description)
                    news_embed = discord.Embed(title=entry.title, description=converted_text, url=entry.link)
                    file_name = await parse_news_img(entry.link, session)
                    if file_name is not None:
                        file = discord.File(f'news/{file_name}', filename=file_name)
                        news_embed.set_image(url=f'attachment://{file_name}')
                        new_thread, new_message  = await channel.create_thread(name=entry.title, embed=news_embed, file=file)
                        await new_thread.edit(locked = True)
                    else:
                        new_thread, new_message = await channel. channel.create_thread(name=entry.title, embed=news_embed)
                        await new_thread.edit(locked = True)

                    