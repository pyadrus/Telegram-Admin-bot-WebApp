import yaml


def load_translations():
    """Загрузка текста для бота"""
    with open("messages/translations.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


translations = load_translations()
