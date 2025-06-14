import discord
from src.short import link_shortener
import xml.etree.ElementTree as ET
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

def safe_float_conversion(value: str, default: float = 0.0) -> float:
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default

def safe_int_conversion(value: str, default: int = 0) -> int:
    try:
        return int(float(value)) if value else default
    except (ValueError, TypeError):
        return default

def format_number(value: float) -> str:
    try:
        return f"{value:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"

def check_is_minion(root: ET.Element) -> bool:
    try:
        show_minion = any(
            input_node.get('boolean') == 'true' 
            for input_node in root.findall(".//Input[@name='showMinion']")
        )
        minion_stat = bool(root.findall(".//MinionStat"))
        return show_minion or minion_stat
    except Exception as e:
        logger.error(f"Error checking minion status: {e}")
        return False

def create_off_str(stats_dict: Dict[str, str], is_minion: bool) -> str:
    try:
        off_lines = ['```ps1']
        off_lines.append('[Minion Stats]' if is_minion else '[Offence]')
        
        damage_stats = [
            ('AverageDamage', 'Hit Damage', format_number),
            ('Speed', 'Attack Speed', lambda x: str(round(safe_float_conversion(x), 2))),
            ('PreEffectiveCritChance', 'Crit Chance', lambda x: f'{x}%'),
            ('CritMultiplier', 'Crit Multi', lambda x: f'{round(safe_float_conversion(x) * 100)}%'),
            ('HitChance', 'Hit Chance', lambda x: f'{x}%'),
            ('TotalDotDPS', 'Total Dot DMG', format_number),
            ('CombinedDPS', 'Total DMG', format_number)
        ]
        
        for stat_key, display_name, formatter in damage_stats:
            value = stats_dict.get(stat_key, '0')
            if value and value != '0':
                try:
                    if stat_key in ['AverageDamage', 'TotalDotDPS', 'CombinedDPS']:
                        formatted_value = format_number(safe_float_conversion(value))
                    else:
                        formatted_value = formatter(value)
                    off_lines.append(f'{display_name}: {formatted_value}')
                except Exception as e:
                    logger.warning(f"Error formatting {stat_key}: {e}")
        
        if is_minion:
            minion_stats = [
                ('Life', 'Minion Life'),
                ('LifeRegenRecovery', 'Minion Regen', lambda x: str(round(safe_float_conversion(x)))),
                ('EnergyShield', 'Minion ES'),
                ('EnergyShieldRegenRecovery', 'Minion ES Regen')
            ]
            
            for stat_key, display_name, *formatter in minion_stats:
                value = stats_dict.get(stat_key, '0')
                if value and value != '0':
                    if formatter:
                        value = formatter[0](value)
                    off_lines.append(f'{display_name}: {value}')
        
        off_lines.append('```')
        return '\n'.join(off_lines)
        
    except Exception as e:
        logger.error(f"Error creating offense string: {e}")
        return "```ps1\n[Offence]\nError loading offense data\n```"

def create_def_str(stats_dict: Dict[str, str]) -> Tuple[str, str]:
    try:
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
        ]
        
        for stat_key, stat_name in def_stats:
            value = stats_dict.get(stat_key, '0')
            def_value = safe_int_conversion(value)
            if def_value != 0:
                def_lines.append(f"{stat_name}: {def_value}")
        
        move_speed_mod = safe_float_conversion(stats_dict.get("EffectiveMovementSpeedMod", "1"))
        def_ms_stat = round(move_speed_mod * 100) - 100
        def_lines.append(f'Movespeed: {def_ms_stat}')
        def_lines.append('```')
        
        def_str = '\n'.join(def_lines)
        lines = def_str.splitlines()
        
        num_lines = len(lines)
        half_num_lines = num_lines // 2
        
        first_half = '\n'.join(lines[:half_num_lines]) + '\n```'
        second_half = '```ps1\n' + '\n'.join(lines[half_num_lines:])
        
        return first_half, second_half
        
    except Exception as e:
        logger.error(f"Error creating defense string: {e}")
        return "```ps1\n[Defence]\nError loading defense data\n```", ""

def create_rgn_str(stats_dict: Dict[str, str]) -> str:
    try:
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
                stat_value = safe_int_conversion(stats_dict[stat_key])
                if stat_value != 0:
                    rgn_lines.append(f"{stat_name}: {stat_value}")
        
        rgn_lines.append('```')
        return '\n'.join(rgn_lines)
        
    except Exception as e:
        logger.error(f"Error creating regen string: {e}")
        return "```ps1\n[Leech|Regen]\nError loading regen data\n```"

def create_res_str(stats_dict: Dict[str, str]) -> str:
    try:
        res_lines = ['```ps1', '[Resists]']
        
        res_stats = [
            ('FireResist', 'Fire'),
            ('ColdResist', 'Cold'),
            ('LightningResist', 'Lightning'),
            ('ChaosResist', 'Chaos')
        ]
        
        for stat_key, stat_name in res_stats:
            value = stats_dict.get(stat_key, '0')
            res_lines.append(f"{stat_name}: {value}")
        
        res_lines.append('```')
        return '\n'.join(res_lines)
        
    except Exception as e:
        logger.error(f"Error creating resist string: {e}")
        return "```ps1\n[Resists]\nError loading resist data\n```"

def create_ehp_str(stats_dict: Dict[str, str]) -> str:
    try:
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
            value = stats_dict.get(stat_key, '0')
            ehp_value = safe_float_conversion(value)
            if ehp_value != 0:
                formatted_value = format_number(ehp_value)
                ehp_lines.append(f"{stat_name}: {formatted_value}")
        
        ehp_lines.append('```')
        return '\n'.join(ehp_lines)
        
    except Exception as e:
        logger.error(f"Error creating eHP string: {e}")
        return "```ps\n[eHP|Max Hit]\nError loading eHP data\n```"

def create_footer(root: ET.Element) -> str:
    try:
        input_tags = root.findall("./Config/Input")
        tags = []
        
        for input_tag in input_tags:
            name = input_tag.get("name")
            value = (input_tag.get("boolean") or 
                    input_tag.get("number") or 
                    input_tag.get("string"))
            if name and value:
                tags.append(f"{name}:{value},")

        tags_string = ''.join(tags)
        
        if not tags_string:
            return "No configuration found"
        
        separator = '\n'
        tags_with_separator = [
            tags_string[i:i + 90] 
            for i in range(0, len(tags_string), 90)
        ]
        
        return separator.join(tags_with_separator).rstrip(',')
        
    except Exception as e:
        logger.error(f"Error creating footer: {e}")
        return "Error loading configuration"

def create_main_embed(link: str, root: ET.Element, stats_dict: Dict[str, str]) -> discord.Embed:
    try:
        main_embed = discord.Embed(title='', description='')

        is_minion = check_is_minion(root)
        
        off_str = create_off_str(stats_dict, is_minion)
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

        try:
            specs = root.findall('.//Spec')[:3]
            urls = []
            
            for spec in specs:
                title = spec.get('title', 'URL')
                tree_version = spec.get('treeVersion', '').replace('_', '.')
                url_elem = spec.find('.//URL')
                
                if url_elem is not None and url_elem.text:
                    short_url = link_shortener(url_elem.text.strip())
                    urls.append(f"[{title} {tree_version}]({short_url})")
            
            if urls:
                main_embed.add_field(name='Tree:', value='\n'.join(urls), inline=True)
            else:
                main_embed.add_field(name='Tree:', value='No tree URLs found', inline=True)
                
        except Exception as e:
            logger.warning(f"Error processing tree URLs: {e}")
            main_embed.add_field(name='Tree:', value='Error loading tree URLs', inline=True)

        main_embed.add_field(name='\u200b', value='\u200b', inline=True)
        
        try:
            short_link = link_shortener(link)
            main_embed.add_field(name='Pastebin:', value=f'[Link]({short_link})', inline=True)
        except Exception as e:
            logger.warning(f"Error shortening pastebin link: {e}")
            main_embed.add_field(name='Pastebin:', value=f'[Link]({link})', inline=True)

        footer_text = create_footer(root)
        main_embed.set_footer(text=footer_text)

        return main_embed
        
    except Exception as e:
        logger.error(f"Error creating main embed: {e}")
        error_embed = discord.Embed(
            title='Error',
            description='Error loading build data',
            color=discord.Color.red()
        )
        return error_embed