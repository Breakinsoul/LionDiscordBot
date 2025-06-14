from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)

def username_splitter(nickname: str) -> Optional[str]:
    try:
        if not nickname or not isinstance(nickname, str):
            logger.warning(f"Invalid nickname input: {nickname}")
            return None
            
        cleaned_nickname = nickname.strip().replace(' ', '')
        
        if not cleaned_nickname:
            logger.warning("Empty nickname after cleaning")
            return None
            
        if '(' in cleaned_nickname:
            username_split = cleaned_nickname.rsplit('(', 1)[0]
        else:
            username_split = cleaned_nickname.rsplit('_', 1)[0]
            
        if not username_split:
            logger.warning(f"Could not extract username from: {nickname}")
            return None
            
        if len(username_split) < 2:
            logger.warning(f"Username too short after splitting: {username_split}")
            return None
            
        if not re.match(r'^[a-zA-Z0-9_]+$', username_split):
            logger.warning(f"Username contains invalid characters: {username_split}")
            return None
            
        return username_split
        
    except Exception as e:
        logger.error(f"Error splitting username '{nickname}': {e}")
        return None