import i18n
import pathlib
from discord import Guild
from discord.ext.commands import Context, Command


class Translator:
    def __init__(self, bot):
        self.bot = bot
        root_path = pathlib.Path(__file__).parent.absolute()
        i18n.load_path.append(root_path)

    @property
    def locales(self):
        return {
            "en": "en",
            "gb": "en",
            "us": "en",
            "uk": "en",
            "es": "es",
            "ru": "ru"
        }

    @property
    def flags(self):
        return ["gb", "es", "ru"]

    @property
    def hidden_locales(self):
        return ["owo"]

    def setup_translation(self, ctx: Context):
        guild_locale = self.get_locale(ctx.guild)

        def translate(text, scope: str = "", **kwargs):
            locale = kwargs.pop("locale", guild_locale)
            return i18n.t(f"{scope or ctx.command.module}.{text}", **kwargs, locale=locale)
        return translate

    def __call__(self, main_scope: str, guild: Guild):
        guild_locale = self.get_locale(guild)

        def translate(text, scope: str = "", **kwargs):
            locale = kwargs.pop("locale", guild_locale)
            return i18n.t(f"{scope or main_scope}.{text}", **kwargs, locale=locale)
        return translate

    def translate_command(self, ctx: Context, command: Command, translation: str):
        locale = self.get_locale(ctx.guild)
        return i18n.t(f"command_docs.{command.qualified_name.replace(' ', '-')}.{translation}", locale=locale)

    def get_locale(self, guild: Guild) -> str:
        guild_settings = self.bot.guild_settings.get_guild(guild)
        if guild_settings is None:
            return "en"
        return guild_settings.locale
