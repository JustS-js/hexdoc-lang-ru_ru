import logging
from pathlib import Path
from zipfile import ZipFile

from github import Github
from hexdoc._cli.utils.args import PropsOption, VerbosityOption
from hexdoc._cli.utils.load import export_metadata, load_common_data
from hexdoc._cli.utils.logging import setup_logging
from hexdoc.core.loader import ModResourceLoader
from hexdoc.minecraft import Tag
from typer import Typer

from .asset_loader import MinecraftAssetLoader
from .minecraft_assets import MinecraftAssetsRepo
from .piston_meta import VersionManifestV2

logger = logging.getLogger(__name__)

CACHE_ROOT = Path(".hexdoc_minecraft")

app = Typer(
    pretty_exceptions_enable=False,
    context_settings={
        "help_option_names": ["--help", "-h"],
    },
)


@app.command()
def fetch(
    version_id: str,
    *,
    verbosity: VerbosityOption = 1,
):
    """Download the Minecraft client jar."""
    setup_logging(verbosity)

    jar_path = CACHE_ROOT / version_id / "client.jar"

    manifest = VersionManifestV2.fetch()
    package = manifest.fetch_package(version_id)
    package.downloads.client.fetch_file(jar_path)

    logger.info("Done.")


@app.command()
def unzip(
    version_id: str,
    *,
    verbosity: VerbosityOption = 1,
):
    """Partially extract the Minecraft client jar."""
    setup_logging(verbosity)

    version_dir = CACHE_ROOT / version_id
    jar_path = version_dir / "client.jar"

    with ZipFile(jar_path) as jar:
        for name in jar.namelist():
            if name.startswith(
                (
                    "assets/minecraft/blockstates/",
                    "assets/minecraft/models/",
                    "assets/minecraft/textures/",
                )
            ):
                jar.extract(name, version_dir / "resources")

    logger.info("Done.")


@app.command()
def export(
    version_id: str,
    *,
    ref: str = "master",
    props_file: PropsOption,
    verbosity: VerbosityOption = 0,
):
    """Export all textures."""
    props, pm, _ = load_common_data(props_file, verbosity)

    loader = ModResourceLoader.clean_and_load_all(
        props,
        pm,
        export=True,
    )

    asset_loader = MinecraftAssetLoader(
        loader=loader,
        asset_url=props.env.asset_url,
        gaslighting_items=Tag.GASLIGHTING_ITEMS.load(loader).value_ids_set,
        repo=MinecraftAssetsRepo(
            github=Github(),
            ref=ref,
            version=version_id,
        ),
    )

    export_metadata(props, pm, loader, asset_loader)


if __name__ == "__main__":
    app()
