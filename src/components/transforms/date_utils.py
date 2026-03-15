import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

MONTHS_BR = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
    'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
    'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
}

def extract_iso_date(text: str) -> Optional[str]:
    """
    Extracts the first occurrence of a date in YYYY-MM-DD format or converts from other formats.
    Handles: 
    - YYYY-MM-DD
    - DD/MM/YYYY
    - "Janeiro de 2027"
    - "Início de 2027"
    - "Final de 2026"
    """
    if not text:
        return None
    
    text_lower = text.lower().strip()
    
    # 1. Try ISO YYYY-MM-DD
    iso_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if iso_match:
        return iso_match.group(0)
    
    # 2. Try DD/MM/YYYY
    br_match = re.search(r'(\d{2})/(\d{2})/(\d{4})', text)
    if br_match:
        d, m, y = br_match.groups()
        return f"{y}-{m}-{d}"
    
    # 3. Try "[Mês] de [Ano]"
    for month_name, month_num in MONTHS_BR.items():
        if month_name in text_lower:
            year_match = re.search(r'20\d{2}', text)
            if year_match:
                year = year_match.group(0)
                return f"{year}-{month_num:02d}-01"

    # 4. Vague descriptions
    year_match = re.search(r'20\d{2}', text)
    if year_match:
        year = year_match.group(0)
        # Prioritize "final de" over "início de" if both present, but usually they are mutually exclusive in a single field
        if "final de" in text_lower or "fim de" in text_lower:
            return f"{year}-12-31"
        if "início de" in text_lower or "começo de" in text_lower:
            return f"{year}-01-01"
        if "meados de" in text_lower:
            return f"{year}-06-15"
    
    return None

def add_business_days(start_date_str: str, days: int) -> Optional[str]:
    """
    Adds business days (skipping Sat/Sun) to an ISO date string.
    """
    try:
        # Validate input format
        if not re.match(r'\d{4}-\d{2}-\d{2}', str(start_date_str)):
            return start_date_str

        current_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        added_days = 0
        while added_days < days:
            current_date += timedelta(days=1)
            if current_date.weekday() < 5:  # Monday to Friday
                added_days += 1
        return current_date.strftime("%Y-%m-%d")
    except Exception as e:
        logger.error(f"Error calculating business days: {e}")
        return start_date_str

def normalize_schedule_dates(cronograma: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Normalizes schedule dates, resolving ranges and relative dates.
    Uses a fuzzy approach to match event names for dependencies.
    """
    if not cronograma:
        return []

    normalized = []
    events_map = {} # Lowercase event name -> ISO date

    for item in cronograma:
        event = item.get("evento", "").strip()
        raw_date = item.get("data", "").strip()
        
        # 0. Pre-process raw_date to handle things like "5 (cinco) dias"
        clean_date_text = re.sub(r'\(.*?\)', '', raw_date).strip()

        # 1. Simple extraction
        iso_date = extract_iso_date(clean_date_text)
        
        # 2. Relative patterns if not directly extracted
        if not iso_date:
            # Pattern: "X dias [úteis] [após|a partir de|da|de] [Evento]"
            # Updated to handle "a partir de/da", "após", "da", "de"
            relative_match = re.search(r'(\d+)\s+dias(\s+úteis)?\s+(?:após|a partir\s+d[aeo]|d[aeo])\s+(.+)', clean_date_text, re.IGNORECASE)
            if relative_match:
                days_to_add = int(relative_match.group(1))
                is_business = bool(relative_match.group(2))
                trigger_text = relative_match.group(3).strip().lower()
                
                # Remove some noise from trigger text
                trigger_text = re.sub(r'publicação\s+d[ao]\s+', '', trigger_text)
                trigger_text = re.sub(r'divulgação\s+d[ao]\s+', '', trigger_text)
                trigger_text = trigger_text.replace("resultado homologado", "homologação").strip()
                
                # Fuzzy look for trigger event in previous events
                trigger_date = None
                trigger_keywords = set(re.findall(r'\w+', trigger_text))
                # Remove common stop words from keywords
                stop_words = {'de', 'da', 'do', 'o', 'a', 'os', 'as', 'em', 'para', 'com', 'no', 'na'}
                important_keywords = trigger_keywords - stop_words
                
                # Sort by reverse length to match most specific first if possible
                for prev_name in sorted(events_map.keys(), key=len, reverse=True):
                    prev_keywords = set(re.findall(r'\w+', prev_name))
                    # If all important keywords are found in the previous event name
                    if important_keywords and important_keywords.issubset(prev_keywords):
                        trigger_date = events_map[prev_name]
                        break
                    # Fallback to simple substring
                    if trigger_text in prev_name:
                        trigger_date = events_map[prev_name]
                        break
                if trigger_date:
                    if is_business:
                        iso_date = add_business_days(trigger_date, days_to_add)
                    else:
                        try:
                            t_date = datetime.strptime(trigger_date, "%Y-%m-%d")
                            new_date = t_date + timedelta(days=days_to_add)
                            iso_date = new_date.strftime("%Y-%m-%d")
                        except:
                            iso_date = raw_date
                else:
                    iso_date = raw_date
            else:
                iso_date = raw_date

        # Add to result
        new_item = {"evento": event, "data": iso_date}
        normalized.append(new_item)
        
        # Store resolved date for future reference
        if iso_date and re.match(r'\d{4}-\d{2}-\d{2}', str(iso_date)):
            events_map[event.lower()] = iso_date

    return normalized
