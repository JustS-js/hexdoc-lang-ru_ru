from importlib.resources import Package

from hexdoc.plugin import (
    HookReturn,
    LoadJinjaTemplatesImpl,
    LoadResourceDirsImpl,
    ModVersionImpl,
    MinecraftVersionImpl,
    hookimpl,
)

import {{ cookiecutter.__project_slug }}

from .__gradle_version__ import GRADLE_VERSION, MINECRAFT_VERSION


class {{ cookiecutter.plugin_classname }}(
    LoadJinjaTemplatesImpl,
    LoadResourceDirsImpl,
    ModVersionImpl,
    MinecraftVersionImpl,
):
    @staticmethod
    @hookimpl
    def hexdoc_mod_version() -> str:
        return GRADLE_VERSION

    @staticmethod
    @hookimpl
    def hexdoc_minecraft_version() -> str:
        return MINECRAFT_VERSION

    @staticmethod
    @hookimpl
    def hexdoc_load_resource_dirs() -> HookReturn[Package]:
        # This needs to be a lazy import because they may not exist when this file is
        # first loaded, eg. when generating the contents of generated.
        from ._export import generated

        return generated
    
    @staticmethod
    @hookimpl
    def hexdoc_load_jinja_templates() -> HookReturn[tuple[Package, str]]:
        return {{ cookiecutter.__project_slug }}, "_templates"
