from typing import Callable, Union, Dict, Awaitable
import i18n
import pathlib
import copy
from discord import Guild
from discord.ext.commands import Context


class Translator:
    locales = {
        "en": "en",
        "gb": "en",
        "us": "en",
        "uk": "en",
        "es": "es",
        "ru": "ru",
        "hi": "hi",
        "fr": "fr",
        "pt": "pt",
        "br": "pt",
        "ms": "ms"
    }

    flags = {
        "gb": "English",
        "es": "Español",
        "ru": "Русский",
        "br": "Português",
    }

    flag_emojis = {flag: "".join(chr(0x1f185+ord(c)) for c in flag) for flag in flags}
    hidden_locales = ["owo", "hi", "fr", "ms"]

    def __init__(self, get_locale: Callable[[Guild], Awaitable[str]]):
        self.get_locale = get_locale
        root_path = pathlib.Path(__file__).parent.absolute()
        i18n.load_path.append(root_path)
        i18n.set("enable_memoization", True)

    def add_locale_commands(self, bot):
        for locale in set(self.locales.values()) | set(self.hidden_locales):
            def inner(locale: str):
                async def run_locale(ctx, *, rest):
                    await bot.process_commands(ctx.message, ctx.prefix, rest, locale)
                return run_locale
            bot.command(hidden=True, name=locale)(inner(locale))

    async def setup_translation(self, ctx: Context, guild_locale: str = None):
        defaults = {
            "locale": (guild_locale or (await self.get_locale(ctx.guild))).strip(" "),
            "locale_flag_emojis": " ".join(self.flag_emojis.values())
        }

        return TranslatorWithContext(defaults, lambda: ctx.command.module)

    def __call__(self, main_scope: str, guild: Union[Guild, str]):
        async def inner():
            if isinstance(guild, str):
                defaults = {
                    "locale": guild.strip(" "),
                    "locale_flag_emojis": " ".join(self.flag_emojis.values())
                }
            else:
                locale = await self.get_locale(guild)
                defaults = {
                    "locale": locale.strip(" "),
                    "locale_flag_emojis": " ".join(self.flag_emojis.values())
                }

            return TranslatorWithContext(defaults, main_scope)
        return inner()


class TranslatorWithContext:
    def __init__(self, defaults: Dict[str, str], scope: Union[str, Callable[[], str]]):
        self.defaults = defaults
        if isinstance(scope, str):
            self.scope = lambda: scope
        else:
            self.scope = scope

    def set_locale(self, locale: str) -> "TranslatorWithContext":
        self.defaults["locale"] = locale
        return self

    def set_scope(self, scope: str) -> "TranslatorWithContext":
        self.scope = lambda: scope
        return self

    def __call__(self, text: str, scope: str = "", **kwargs):
        return i18n.t(f"{scope or self.scope()}.{text}", **{**self.defaults, **kwargs})

    def __enter__(self):
        return copy.deepcopy(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
