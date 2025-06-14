import discord
import xml.etree.ElementTree as ET
import os
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

def get_enabled_gems(root: ET.Element, skill_number: str) -> str:
    try:
        skills_elem = root.find('Skills')
        if skills_elem is None:
            return "No skills found"
            
        active_skill_set = skills_elem.get('activeSkillSet', '0')
        xpath = f"./Skills/SkillSet[@id='{active_skill_set}']/Skill[{skill_number}]/Gem[@enabled='true']"
        gems = root.findall(xpath)
        
        if not gems:
            return "No enabled gems found"
            
        gem_names = []
        for gem in gems:
            name_spec = gem.get('nameSpec', 'Unknown Gem')
            gem_names.append(name_spec)
            
        return " - ".join(gem_names) if gem_names else "No gem names available"
        
    except Exception as e:
        logger.error(f"Error getting enabled gems: {e}")
        return "Error retrieving gems"

def create_dps_footer_str(root: ET.Element) -> str:
    try:
        skill_number_elem = root.find("./Calcs/Input[@name='skill_number']")
        if skill_number_elem is None:
            return "```ps1\n[Main Skill(s)]\nNo skill selected\n```"
            
        skill_number = skill_number_elem.get('number', '1')
        gems_str = get_enabled_gems(root, skill_number)
        
        return f"```ps1\n[Main Skill(s)]\n{gems_str}\n```"
        
    except Exception as e:
        logger.error(f"Error creating DPS footer: {e}")
        return "```ps1\n[Main Skill(s)]\nError loading skills\n```"

def create_full_dps(stats_dict: Dict[str, str], root: ET.Element) -> str:
    try:
        full_dps = stats_dict.get('FullDPS', '0')
        if full_dps == '0':
            return "```ps1\n[Full DPS]\nNo DPS data available\n```"
            
        try:
            full_dps_value = float(full_dps)
            formatted_dps = f"{full_dps_value:,.0f}".replace(",", ".")
        except ValueError:
            formatted_dps = full_dps
            
        full_dps_lines = [
            "```ps1",
            f"[Full DPS|{formatted_dps}]"
        ]
        
        excluded_stats = {"Best Ignite DPS", "Full Culling DPS"}
        
        for skill in root.iter('FullDPSSkill'):
            stat_name = skill.get("stat")
            stat_value = skill.get("value")
            
            if stat_name not in excluded_stats and stat_name and stat_value:
                try:
                    value_float = float(stat_value)
                    formatted_value = f"{value_float:,.0f}".replace(",", ".")
                    full_dps_lines.append(f"{stat_name}: {formatted_value}")
                except ValueError:
                    full_dps_lines.append(f"{stat_name}: {stat_value}")
        
        full_dps_lines.append("```")
        return '\n'.join(full_dps_lines)
        
    except Exception as e:
        logger.error(f"Error creating full DPS display: {e}")
        return "```ps1\n[Full DPS]\nError loading DPS data\n```"

def create_avatar_file(root: ET.Element) -> Optional[discord.File]:
    try:
        build_elements = root.findall(".//Build")
        if not build_elements:
            logger.warning("No Build elements found in XML")
            return None
            
        for elem in build_elements:
            ascend_class = elem.get('ascendClassName')
            if ascend_class:
                avatar_path = f"icons/{ascend_class}_avatar.webp"
                
                if os.path.exists(avatar_path):
                    return discord.File(avatar_path, filename="image.webp")
                else:
                    logger.warning(f"Avatar file not found: {avatar_path}")
                    
        default_avatar = "icons/default_avatar.webp"
        if os.path.exists(default_avatar):
            return discord.File(default_avatar, filename="image.webp")
            
        return None
        
    except Exception as e:
        logger.error(f"Error creating avatar file: {e}")
        return None

def create_embed_header(root: ET.Element, stats_dict: Dict[str, str]) -> discord.Embed:
    try:
        build_elements = root.findall(".//Build")
        
        if build_elements:
            class_info = []
            for elem in build_elements:
                class_name = elem.get('className', 'Unknown')
                ascend_class = elem.get('ascendClassName', 'Unknown')
                class_info.append(f"[{class_name}|{ascend_class}]")
            asc_str = f"```ps1\n{chr(10).join(class_info)}\n```"
        else:
            asc_str = "```ps1\n[Unknown Class|Unknown Ascendancy]\n```"
            
        embed_header = discord.Embed(title='\u3000', description=asc_str)
        
        dps_footer = create_dps_footer_str(root)
        embed_header.add_field(name='', value=dps_footer, inline=False)
        
        full_dps_value = stats_dict.get('FullDPS', '0')
        if full_dps_value and full_dps_value != "0":
            full_dps_display = create_full_dps(stats_dict, root)
            embed_header.add_field(name='', value=full_dps_display, inline=False)
            
        return embed_header
        
    except Exception as e:
        logger.error(f"Error creating embed header: {e}")
        error_embed = discord.Embed(
            title='Error',
            description='```ps1\nError loading build data\n```',
            color=discord.Color.red()
        )
        return error_embed