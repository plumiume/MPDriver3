def main():

    from typing import TypedDict
    import importlib
    from pathlib import Path
    from multiprocessing import freeze_support
    import textwrap

    from .core.args_base import AppArgs, AppMainModule, _root_argparser, subparsers

    freeze_support()

    PACKAGE_ROOT = Path(__file__).parent

    class AppModuleSpec(TypedDict):
        args: str
        main: str

    app_module_speces = {
        app_module.name: AppModuleSpec(
            args = f".{(app_module / 'args').as_posix().replace('/', '.')}",
            main = f".{(app_module / 'main').as_posix().replace('/', '.')}"
        )
        for app_dir in PACKAGE_ROOT.glob("apps/*")
        if (app_module := app_dir.relative_to(PACKAGE_ROOT)).name[0] != "_" and app_dir.is_dir()
    }

    for app_name in app_module_speces:
        importlib.import_module(app_module_speces[app_name]['args'], PACKAGE_ROOT.name)

    subparsers.help = textwrap.dedent(f"""
        サブコマンド。以下のコマンドが使用できます
        {', '.join(subparsers._name_parser_map.keys())}
    """).strip()

    namespace: AppArgs = _root_argparser.parse_args()

    target_app: AppMainModule = importlib.import_module(app_module_speces[namespace.command]['main'], PACKAGE_ROOT.name)
    target_app.app_main(namespace)

if __name__ == "__main__":
    main()