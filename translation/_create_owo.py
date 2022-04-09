import i18n
from TextToOwO.owo import text_to_owo
import re

sub_func = re.compile(r"\{(\d+)\}")

ignored_translations = ("example_images",)


def create_owo():
    translations = i18n.translations.container
    owo = translations["owo"] = {}
    for translation_name, text in translations["en"].items():
        if translation_name.startswith(ignored_translations):
            owo[translation_name] = text
        elif isinstance(text, str):
            owo[translation_name] = owo_ise(text)
        elif isinstance(text, dict):
            owo[translation_name] = {k: owo_ise(v) for k, v in text.items()}
        else:
            raise AssertionError("Translations must be either str or dict")


def owo_ise(text):
    groups = []
    i = -1

    def _inner(g):
        nonlocal i
        groups.append(g.group())
        i += 1
        return f"{{{i}}}"
    subbed = i18n.translator.TranslationFormatter.pattern.sub(_inner, text)
    owoed = text_to_owo(subbed)

    return sub_func.sub(lambda g: groups[int(g.group(1))], owoed)

