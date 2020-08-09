from typing import Callable
import i18n
import pathlib
from discord import Guild
from discord.ext.commands import Context, Command


class Translator:
    def __init__(self, get_locale: Callable[[Guild], str]):
        self.get_locale = get_locale
        root_path = pathlib.Path(__file__).parent.absolute()
        i18n.load_path.append(root_path)
        i18n.set("enable_memoization", True)

    def add_locale_commands(self, bot):
        for locale in set(self.locales.values()) | set(self.hidden_locales):
            def inner(locale: str):
                async def run_locale(ctx, *, rest):
                    message = ctx.message
                    message.content = ctx.prefix + rest
                    await bot.process_commands(message, ctx.prefix, None, locale)
                return run_locale
            bot.command(hidden=True, name=locale)(inner(locale))

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
        return {
            "gb": "English",
            "es": "Español",
            "ru": "Русский"
        }

    @property
    def hidden_locales(self):
        return ["owo"]

    def setup_translation(self, ctx: Context, guild_locale: str = None):
        if guild_locale is None:
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
