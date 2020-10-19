import yaml
from pathlib import Path

files = {}


def set_data(filename, translation, data):
    if translation not in data:
        raise ValueError(f"{filename}.{translation}.yml must begin with `{translation}:`")
    if filename not in files:
        files[filename] = {}
    files[filename][translation] = data[translation]


for yml_file in Path(__file__).parent.rglob("*.yml"):
    print(f"Loading {yml_file}")
    with open(yml_file, "r", encoding="utf-8") as yml:
        filename, translation, _ = yml_file.name.split(".")
        data = yaml.safe_load(yml)
        set_data(filename, translation, data)
print("All files loaded successfully!")
