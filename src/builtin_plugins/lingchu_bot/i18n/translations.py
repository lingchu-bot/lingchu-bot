# translations.py
translations = {
    "en": {
        "hello": "Hello",
        "welcome": "Welcome, {name}!",
    },
    "zh": {
        "hello": "你好",
        "welcome": "欢迎, {name}!",
    },
}


def t(key: str, lang: str = "en", **kwargs: str) -> str:
    """最简单的翻译函数"""
    try:
        text = translations[lang][key]
    except KeyError:
        text = translations["en"].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
