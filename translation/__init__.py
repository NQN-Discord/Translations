from typing import Callable, Union, Dict, Awaitable, Optional
import i18n
import unidecode
import pathlib
import copy
import inspect
from discord import Guild, Locale
from discord.app_commands.transformers import CommandParameter
from discord.ext.commands import Context
from discord.app_commands import locale_str, TranslationContext, Command, Group, ContextMenu
from discord.app_commands import Translator as DpyTranslator

from _singleton import Singleton
from ._create_owo import create_owo
from ._ruamel_loader import YamlLoader


try:
    from prometheus_client import Counter
except ImportError:
    translate_function = None
else:
    keys_used = Counter(
        "keys_used",
        "Translation keys used",
        labelnames=["key"],
        namespace="translation"
    )

    def translate_function(key, **kwargs):
        keys_used.labels(key=key).inc()
        return i18n.t(key, **kwargs)


class DpyNQNTranslator(DpyTranslator):
    discord_locale_map = {
        Locale.american_english: "en",
        Locale.british_english: "en",
        Locale.french: "fr",
        Locale.german: "de",
        Locale.italian: "it",
        Locale.brazil_portuguese: "pt",
        Locale.russian: "ru",
        Locale.spain_spanish: "es",

    }
    _param_contexts = (
        TranslationContext.parameter_name,
        TranslationContext.parameter_description,
        TranslationContext.choice_name
    )

    async def load(self):
        self._translator = Translator()

    async def translate(self, string: locale_str, locale: Locale, context: TranslationContext, *, command: Command = None, parameter: CommandParameter = None) -> Optional[str]:
        nqn_locale = self.discord_locale_map.get(locale)
        if nqn_locale is None:
            return

        if command is None:
            # Temporary
            parameter = None
            frame = inspect.currentframe()
            while True:
                _self = frame.f_locals.get("self")
                if isinstance(_self, CommandParameter):
                    parameter = _self
                if isinstance(_self, (Command, Group, ContextMenu)):
                    command = _self
                    break
                frame = frame.f_back

        if context == TranslationContext.choice_name and parameter.name in command.extras.get("choice_overrides", {}):
            key_prefix = command.extras["choice_overrides"][parameter.name]
            translation_key = string
        else:
            if "param_overrides" in command.extras and context in self._param_contexts:
                key_prefix = f"command_docs.{command.extras['param_overrides']}"
            else:
                key_prefix = f"command_docs.{command.extras['translation_key']}"

            match context:
                case TranslationContext.command_name:
                    translation_key = "name"
                case TranslationContext.command_description:
                    translation_key = "short_doc"
                case TranslationContext.parameter_name:
                    translation_key = f"params.{parameter.name}.name"
                case TranslationContext.parameter_description:
                    translation_key = f"params.{parameter.name}.description"
                case TranslationContext.choice_name:
                    translation_key = f"params.{parameter.name}.choices.{string}"
                case _:
                    raise NotImplementedError("Translation key")
        scope = self._translator.with_scope(key_prefix, nqn_locale)

        translated = scope(translation_key)
        assert not translated.startswith("command_docs")
        if context == TranslationContext.command_description:
            return translated[:100]
        return translated


class Translator(metaclass=Singleton):
    locales = {
        "en": "en",
        "gb": "en",
        "us": "en",
        "uk": "en",
        "de": "de",
        "es": "es",
        "ru": "ru",
        "hi": "hi",
        "fr": "fr",
        "pt": "pt",
        "br": "pt",
        "ms": "ms",
        "it": "it",
        "vi": "vi",
        "fa": "fa"
    }

    locale_flags = {
        "en": "gb",
        "es": "es",
        "ru": "ru",
        "pt": "br",
        "it": "it",
        "vi": "vn",
        "fa": "ir"
    }

    flag_emojis = {locale: "".join(chr(0x1f185+ord(c)) for c in flag_name) for locale, flag_name in locale_flags.items()}
    hidden_locales = ["owo", "hi", "fr", "ms"]
    supported_locales = {*locales.values(), *hidden_locales}

    def __init__(self):
        self.get_locale = None
        root_path = pathlib.Path(__file__).parent
        i18n.load_path.append(root_path.absolute())
        i18n.set("enable_memoization", True)
        i18n.set("skip_locale_root_data", True)
        i18n.resource_loader.register_loader(YamlLoader, ["yml"])

        for path in root_path.rglob("*.yml"):
            locale = path.parent.name
            translations_dic = i18n.resource_loader.load_resource(str(path), None)
            i18n.resource_loader.load_translation_dic(translations_dic, "", locale)

        create_owo()
        if translate_function:
            self.translate_function = translate_function
        else:
            self.translate_function = i18n.t

    def set_get_locale(self, get_locale: Callable[[Guild], Awaitable[str]]):
        self.get_locale = get_locale

    def add_locale_commands(self, bot):
        for locale in self.supported_locales:
            if locale != "owo":
                # Some of the translations for owo are kind of rude/nonsensical. Lets not add these as commands
                for command in bot.walk_commands():
                    translated_name = self.translate_function(f"command_docs.{command.qualified_name.replace(' ', '-')}.name", locale=locale)
                    if translated_name.startswith("command_docs"):
                        continue
                    for name in [translated_name, unidecode.unidecode(translated_name)]:
                        if name == command.name or name in command.aliases:
                            continue
                        command.aliases.append(name)
                        if command.parent is None:
                            if bot.all_commands.get(name) not in (None, command):
                                raise AssertionError("Command duplicated with translation")
                            bot.all_commands[name] = command

            def inner(locale: str):
                async def run_locale(ctx, *, rest):
                    await bot.process_commands(ctx.message, ctx.prefix, rest, locale_override=locale)
                return run_locale
            bot.command(hidden=True, name=locale)(inner(locale))

    async def setup_translation(self, ctx: Context, guild_locale: str = None):
        if guild_locale is None:
            try:
                guild_locale = ctx.guild_settings.locale
            except AttributeError:
                pass
            if guild_locale is None:
                guild_locale = await self.get_locale(ctx.guild)
        defaults = {
            "locale": guild_locale.strip(" "),
            "locale_flag_emojis": " ".join(self.flag_emojis.values())
        }

        return TranslatorWithContext(defaults, lambda: ctx.command.module, translate_function=self.translate_function)

    def with_scope(self, scope: str, locale: str) -> "TranslatorWithContext":
        return TranslatorWithContext({"locale": locale}, scope=scope, translate_function=self.translate_function)

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

            return TranslatorWithContext(defaults, main_scope, translate_function=self.translate_function)
        return inner()


class TranslatorWithContext:
    def __init__(self, defaults: Dict[str, str], scope: Union[str, Callable[[], str]], translate_function):
        self.defaults = defaults
        if isinstance(scope, str):
            self.scope = lambda: scope
        else:
            self.scope = scope
        self._translate_function = translate_function

    def set_locale(self, locale: str) -> "TranslatorWithContext":
        self.defaults["locale"] = locale
        return self

    def set_scope(self, scope: str) -> "TranslatorWithContext":
        self.scope = lambda: scope
        return self

    def __call__(self, text: str, scope: str = "", **kwargs):
        return self._translate_function(f"{scope or self.scope()}.{text}", **{**self.defaults, **kwargs})

    def __enter__(self):
        return copy.deepcopy(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
