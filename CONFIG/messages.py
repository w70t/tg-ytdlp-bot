from CONFIG.LANGUAGES.messages_AR import messages_AR
from CONFIG.LANGUAGES.messages_EN import messages_EN
from CONFIG.LANGUAGES.messages_IN import messages_IN
from CONFIG.LANGUAGES.messages_RU import messages_RU

LANGUAGES = {
    "ar": messages_AR,
    "en": messages_EN,
    "in": messages_IN,
    "ru": messages_RU,
}

def get_messages_instance(user_id=None, language_code=None):
    """
    Get the appropriate messages class based on user language.
    """
    lang = language_code.lower() if language_code and language_code.lower() in LANGUAGES else "en"
    return LANGUAGES.get(lang, messages_EN)()

class Messages:
    @classmethod
    def all_keys(cls):
        return [attr for attr in dir(cls) if not attr.startswith("__")]

    @classmethod
    def get(cls, key):
        return getattr(cls, key, f"[{key}]")
