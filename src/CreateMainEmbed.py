import discord
from src.short import link_shortener
def check_is_minion(root):
    show_minion = any(input_node.get('boolean') == 'true' for input_node in root.findall(".//Input[@name='showMinion']"))
    minion_stat = bool(root.findall(".//MinionStat"))
    return show_minion or minion_stat

def create_off_str(stats_dict,is_minion):
    off_lines = ['```ps1']
    if is_minion:
        off_lines.append('[Minion Stats]')
    else:
        off_lines.append('[Offence]')
    
    if 'AverageDamage' in stats_dict:
        if stats_dict['AverageDamage'] != '0':
            off_hit_dmg = '{:,.0f}'.format(float(stats_dict['AverageDamage'])).replace(',', '.')
            off_lines.append(f'Hit Damage: {off_hit_dmg}')
    if 'Speed' in stats_dict:
        if stats_dict['Speed'] != '0':
            off_as = round(float(stats_dict["Speed"]),2)
            off_lines.append(f'Attack Speed: {off_as}')
    if 'PreEffectiveCritChance' in stats_dict:
        if stats_dict['PreEffectiveCritChance'] != '0':
            off_crit_chance = f'{stats_dict["PreEffectiveCritChance"]}%'
            off_lines.append(f'Crit Chance: {off_crit_chance}')
    if 'CritMultiplier' in stats_dict:
        if stats_dict['CritMultiplier'] != '0':
            off_crit_multi = f'{round(float(stats_dict["CritMultiplier"]) * 100)}%'
            off_lines.append(f'Crit Multi: {off_crit_multi}')
    if 'HitChance' in stats_dict:
        if stats_dict['HitChance'] != '0':
            off_lines.append(f'Hit Chance: {stats_dict["HitChance"]}%')
    if 'TotalDotDPS' in stats_dict:
        if stats_dict['TotalDotDPS'] != '0':
            off_dot_dps = '{:,.0f}'.format(float(stats_dict['TotalDotDPS'])).replace(',', '.')
            off_lines.append(f'Total Dot DMG: {off_dot_dps}')
    if 'CombinedDPS' in stats_dict:    
        if stats_dict['CombinedDPS'] != '0':
            off_total_dmg = '{:,.0f}'.format(float(stats_dict['CombinedDPS'])).replace(',', '.')
            off_lines.append(f'Total DMG: {off_total_dmg}')
    
    if is_minion:
        if 'Life' in stats_dict:
                off_lines.append(f'Minion Life: {stats_dict["Life"]}')
        if 'LifeRegenRecovery' in stats_dict:
                minion_life_reg = round(float(stats_dict["LifeRegenRecovery"]))
                off_lines.append(f'Minion Regen: {minion_life_reg}')
        if 'EnergyShield' in stats_dict:
            if stats_dict["EnergyShield"] != '0':
                off_lines.append(f'Minion ES: {stats_dict["EnergyShield"]}')
        if 'EnergyShieldRegenRecovery' in stats_dict:
            if stats_dict['EnergyShieldRegenRecovery'] != '0':
                off_lines.append(f'Minion ES Regen: {stats_dict["EnergyShieldRegenRecovery"]}')
    off_lines.append('```')
    return '\n'.join(off_lines)

def create_def_str(stats_dict):
    def_lines = ['```ps1', '[Defence]']
    def_stats = [
        ('Life', 'Life'),
        ('LifeUnreserved', 'Life Unres'),
        ('Mana', 'Mana'),
        ('ManaUnreserved', 'Mana Unres'),
        ('EnergyShield', 'Energy Shield'),
        ('Armour', 'Armour'),
        ('Evasion', 'Evasion'),
        ('Ward', 'Ward'),
        ('ProjectileEvadeChance', 'Projectile Evade'),
        ('MeleeEvadeChance', 'Melee Evade'),
        ('BlockChance', 'Block Chance'),
        ('SpellBlockChance', 'Spell Block'),
        ('AttackDodgeChance', 'Attack Dodge'),
        ('SpellDodgeChance', 'Spell Dodge'),
        ('SpellSuppressionChance', 'Spell Suppres'),
        ('SpellDodgeChance', 'Spell Dodge'),
        ('AttackDodgeChance', 'Attack Dodge'),
    ]
    for stat_key, stat_name in def_stats:
        def_value = round(float(stats_dict[stat_key]))
        if def_value != 0:
            def_lines.append(f"{stat_name}: {def_value}")
    def_ms_stat = round(float(stats_dict["EffectiveMovementSpeedMod"]) * 100) - 100
    def_lines.append(f'Movespeed: {def_ms_stat}')
    def_lines.append('```')
    
    def_str = '\n'.join(def_lines)
    lines = def_str.splitlines()
    
    num_lines = len(lines)
    half_num_lines = num_lines // 2
    first_half = '\n'.join(lines[:half_num_lines])
    first_half += '\n```'
    
    second_half = '```ps1\n'
    second_half += '\n'.join(lines[half_num_lines:])
    
    return first_half,second_half

def create_rgn_str(stats_dict):
    rgn_lines = ['```ps1', '[Leech|Regen]']
    leech_regen_stats = [
        ('LifeLeechGainRate', 'Life Leech'),
        ('TotalNetRegen', 'Net Regen'),
        ('ManaLeechGainRate', 'Mana Leech'),
        ('EnergyShieldLeechGainRate', 'Energy Shield Leech'),
        ('LifeRegenRecovery', 'Life Regen'),
        ('ManaRegenRecovery', 'Mana Regen'),
        ('EnergyShieldRegenRecovery', 'Energy Shield Regen'),
        ('RageRegenRecovery', 'Rage Regen')
    ]
    for stat_key, stat_name in leech_regen_stats:
        if stat_key in stats_dict:
            stat_value = round(float(stats_dict[stat_key]))
            if stat_value != 0:
                rgn_lines.append(f"{stat_name}: {stat_value}")
    rgn_lines.append('```')
    return '\n'.join(rgn_lines)
    
def create_res_str(stats_dict):
    res_lines = ['```ps1', '[Resists]']
    res_stats = [
        ('FireResist', 'Fire'),
        ('ColdResist', 'Cold'),
        ('LightningResist', 'Lightning'),
        ('ChaosResist', 'Chaos')
    ]
    for stat_key, stat_name in res_stats:
        res_lines.append(f"{stat_name}: {stats_dict[stat_key]}")
    res_lines.append('```')
    return '\n'.join(res_lines)

def create_ehp_str(stats_dict):
    ehp_lines = ['```ps', '[eHP|Max Hit]']
    ehp_stats = [
        ('TotalEHP', 'TotalEHP'),
        ('PhysicalMaximumHitTaken', 'Phys'),
        ('LightningMaximumHitTaken', 'Light'),
        ('FireMaximumHitTaken', 'Fire'),
        ('ColdMaximumHitTaken', 'Cold'),
        ('ChaosMaximumHitTaken', 'Chaos')
    ]
    for stat_key, stat_name in ehp_stats:
        ehp_value = f'{float(stats_dict[stat_key]):,.0f}'
        if ehp_value != 0:
            ehp_value = ehp_value.replace(",", ".")
            ehp_lines.append(f"{stat_name}: {ehp_value}")
    ehp_lines.append('```')
    return '\n'.join(ehp_lines)

def create_footer(root):
    # Find all <Input> tags within the <Config> tag
    input_tags = root.findall("./Config/Input")
    tags = []
    # Print the name and value for each <Input> tag
    for input_tag in input_tags:
        name = input_tag.get("name")
        value = input_tag.get("boolean") or input_tag.get("number") or input_tag.get("string")
        tags.append(f"{name}:{value},")

    tags_string = ''.join(tags)

    # Insert the separator every 83 characters
    separator = '\n'  # Здесь можно задать нужный вам символ разделителя
    tags_with_separator = [tags_string[i:i + 90] for i in range(0, len(tags_string), 90)]
    result = separator.join(tags_with_separator).rstrip(',')
    return result            

def create_main_embed(link, root, stats_dict):
    main_embed = discord.Embed(title='', description='')

    off_str = create_off_str(stats_dict, check_is_minion(root))
    def_first_half, def_second_half = create_def_str(stats_dict)
    rgn_str = create_rgn_str(stats_dict)
    res_str = create_res_str(stats_dict)
    ehp_str = create_ehp_str(stats_dict)

    main_embed.add_field(name='', value=off_str, inline=True)
    main_embed.add_field(name='', value=rgn_str, inline=True)
    main_embed.add_field(name='', value=ehp_str, inline=True)
    main_embed.add_field(name='', value=def_first_half, inline=True)
    main_embed.add_field(name='', value=def_second_half, inline=True)
    main_embed.add_field(name='', value=res_str, inline=True)
    main_embed.add_field(name='', value='', inline=False)

    urls = [f"[{spec.get('title', 'URL')} {spec.get('treeVersion').replace('_', '.')}]({link_shortener(spec.find('.//URL').text.strip())})" for spec in root.findall('.//Spec')[:3]]
    result = '\n'.join(urls)
    main_embed.add_field(name='Tree:', value=result, inline=True)

    main_embed.add_field(name='\u200b', value=f'\u200b', inline=True)
    short_link = link_shortener(link)
    main_embed.add_field(name='Pastebin:', value=f'[Link]({short_link})', inline=True)
    main_embed.set_footer(text=create_footer(root))

    return main_embed
