from ruamel import yaml
from ruamel.yaml.parser import ParserError

from i18n.loaders.loader import Loader, I18nFileLoadError


class YamlLoader(Loader):
    """class to load yaml files"""
    def __init__(self):
        super(YamlLoader, self).__init__()

    def parse_file(self, file_content):
        try:
            return yaml.load(file_content, Loader=yaml.SafeLoader)
        except ParserError as e:
            raise I18nFileLoadError("Invalid YAML file") from e
