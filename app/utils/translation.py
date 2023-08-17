import json

def load_translation(language):
    primary_language = language.split(",")[0].split(";")[0].split("-")[0]
    print(f"Primary: {primary_language}")
    translations = {}
    try:
        with open(f"locales/{primary_language}.json", "r", encoding="utf-8") as f:
            translations = json.load(f)
    except FileNotFoundError:
        pass
    print(f"Loaded translations for {language}: {translations}")
    return translations