import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def load_translation(language):
    primary_language = language.split(",")[0].split(";")[0].split("-")[0]
    translations = {}
    try:
        with open(f"locales/{primary_language}.json", "r", encoding="utf-8") as f:
            translations = json.load(f)
    except FileNotFoundError:
        pass
    logger.info(f"Loaded translations for {language}")
    return translations