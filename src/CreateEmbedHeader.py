import discord

def get_enabled_gems(root, skill_number):
    skills_elem = root.find('Skills')
    active_skill_set = skills_elem.get('activeSkillSet')
    gems = root.findall(f"./Skills/SkillSet[@id='{active_skill_set}']/Skill[{skill_number}]/Gem[@enabled='true']")
    gems_str = " - ".join(gem.get('nameSpec') for gem in gems)
    return gems_str

def create_dps_footer_str(root):
    skill_number = root.find("./Calcs/Input[@name='skill_number']").get('number')
    gems_str = get_enabled_gems(root, skill_number)
    dps_footer_str = [
        '```ps1',
        '[Main Skill(s)]',
        gems_str,
        '```'
    ]
    return '\n'.join(dps_footer_str)

def create_full_dps(stats_dict,root):
    full_dps_str = ['```ps1']
    full_dps_str.append(f"[Full Dps|{float(stats_dict['FullDPS']):,.0f}]")
    full_str = "\n".join([f"{skill.get('stat')}: {float(skill.get('value')):,.0f}".replace(",", ".") for skill in root.iter('FullDPSSkill') if skill.get("stat") not in ["Best Ignite DPS", "Full Culling DPS"]])
    full_dps_str.append(full_str)
    full_dps_str.append('```')
    return '\n'.join(full_dps_str)

def create_avatar_file(root):
    elements = [elem for elem in root.findall(".//Build")]
    for elem in elements:
            return discord.File(f"icons/{elem.get('ascendClassName')}_avatar.webp", filename="image.webp") 

def create_embed_header(root, stats_dict):
    elements = [f"[{elem.get('className')}|{elem.get('ascendClassName')}]" for elem in root.findall(".//Build")]
    asc_str = '```ps1\n' + '\n'.join(elements) + '\n```'
    embed_header = discord.Embed(title='\u3000', description=asc_str)
    embed_header.add_field(name='', value=create_dps_footer_str(root), inline=False)
    if stats_dict['FullDPS'] != "0":
        embed_header.add_field(name='', value=create_full_dps(stats_dict, root), inline=False)
    return embed_header
