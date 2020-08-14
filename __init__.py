from typing import Callable, Union
import i18n
import pathlib
from discord import Guild
from discord.ext.commands import Context


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
            #"ru": "Русский"
        }

    @property
    def flag_emojis(self):
        return " ".join(f":flag_{flag}:" for flag in self.flags)

    @property
    def hidden_locales(self):
        return ["owo"]

    def setup_translation(self, ctx: Context, guild_locale: str = None):
        defaults = {
            "locale": (guild_locale or self.get_locale(ctx.guild)).strip(" "),
            "locale_flag_emojis": self.flag_emojis
        }

        def translate(text, scope: str = "", **kwargs):
            return i18n.t(f"{scope or ctx.command.module}.{text}", **{**defaults, **kwargs})
        return translate

    def __call__(self, main_scope: str, guild: Union[Guild, str]):
        if isinstance(guild, str):
            defaults = {
                "locale": guild,
                "locale_flag_emojis": self.flag_emojis
            }
        else:
            defaults = {
                "locale": self.get_locale(guild),
                "locale_flag_emojis": self.flag_emojis
            }

        def translate(text, scope: str = "", **kwargs):
            return i18n.t(f"{scope or main_scope}.{text}", **{**defaults, **kwargs})
        return translate