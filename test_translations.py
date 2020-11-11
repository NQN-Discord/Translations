import yaml
from pathlib import Path
import traceback
from tabulate import tabulate

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


def get_translation_values(content):
    if isinstance(content, str):
        return {""}
    return {f"{k}{i and '.'}{i}" for k, v in content.items() for i in get_translation_values(v)}


def get_stats(file):
    current_file = {}
    for tr, content in file.items():
        if tr not in current_file:
            current_file[tr] = 0
        count = get_translation_counts(content)
        current_file[tr] += count

    max_count = max(current_file.values())
    for k, v in current_file.items():
        current_file[k] = f"{v} ({round(100*v/max_count)}%)"

    return current_file


def get_missing(file):
    current_file = {}
    for tr, content in file.items():
        if tr not in current_file:
            current_file[tr] = set()
        current_file[tr] |= get_translation_values(content)
    all_translations = {i for tr in current_file.values() for i in tr}
    missing = {tr: all_translations - v for tr, v in current_file.items()}

    return missing


def main():
    base_file = Path(__file__).parent
    for yml_file in base_file.rglob("*.yml"):
        print(f"Loading {yml_file}")
        with open(yml_file, "r", encoding="utf-8") as yml:
            filename, translation, _ = ".".join(yml_file.relative_to(base_file).parts).rsplit(".", 2)
            data = yaml.safe_load(yml)
            set_data(filename, translation, data)

    langs = set()
    for f in files.values():
        langs.update(f.keys())
    langs = list(sorted(langs))
    stats = []
    missing_translations = set()
    for file, data in files.items():
        f_stats = get_stats(data)
        missing = get_missing(data)
        if missing.get("ru"):
            missing_translations |= {f"{file}.{i}" for i in missing["ru"]}
        row = [file]
        for header in langs:
            if header in f_stats:
                row.append(f_stats[header])
            else:
                row.append("-")
        stats.append(row)
    #print("\n".join(sorted(missing_translations)))
    print(tabulate(stats, headers=langs))

    print("All files loaded successfully!")


try:
    main()
except Exception as e:
    traceback.print_exc()
finally:
    input("Press Enter to exit")
