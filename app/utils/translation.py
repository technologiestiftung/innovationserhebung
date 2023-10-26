import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# HTML_TAGS = {
#     "<strong>": "\u003cstrong\u003e",
#     "</strong>": "\u003c/strong\u003e",
#     "<br>": "\u003cbr/\u003e",
# }

def load_translation(language):
    primary_language = language.split(",")[0].split(";")[0].split("-")[0]
    translations = {}
    try:
        with open(f"locales/{primary_language}.json", "r", encoding="utf-8") as f:
            translations = json.load(f)
            # TODO: Remove this if it is no longer needed.
            # for key in translations:
            #     if isinstance(translations[key], str):
            #         for tag, escape_sequence in HTML_TAGS.items():
            #             translations[key] = translations[key].replace(tag, escape_sequence)
    except FileNotFoundError:
        pass
    logger.info(f"Loaded translations for {language}")
    return translations
