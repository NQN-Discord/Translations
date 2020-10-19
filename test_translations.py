import yaml
from pathlib import Path
import traceback

files = {}


def set_data(filename, translation, data):
    if translation not in data:
        raise ValueError(f"{filename}.{translation}.yml must begin with `{translation}:`")
    if filename not in files:
        files[filename] = {}
    files[filename][translation] = data[translation]


def get_translation_counts(content):
    if isinstance(content, str):
        return 1
    return sum(get_translation_counts(v) for v in content.values())


def show_stats():
    langs = {}
    for file in files.values():
        for tr, content in file.items():
            if tr not in langs:
                langs[tr] = 0
            langs[tr] += get_translation_counts(content)

    max_count = max(langs.values())
    for lang, count in langs.items():
        print(f"{lang}: {count} lines translated ({round(100*count/max_count)}%)")


def main():
    for yml_file in Path(__file__).parent.rglob("*.yml"):
        print(f"Loading {yml_file}")
        with open(yml_file, "r", encoding="utf-8") as yml:
            filename, translation, _ = yml_file.name.split(".")
            data = yaml.safe_load(yml)
            set_data(filename, translation, data)

    print("All files loaded successfully!")
    show_stats()


try:
    main()
except Exception as e:
    traceback.print_exc()
finally:
    input("Press Enter to exit")
