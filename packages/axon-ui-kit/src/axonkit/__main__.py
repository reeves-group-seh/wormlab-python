# std
from argparse import ArgumentParser, Namespace
from enum import StrEnum
from typing import Any


class Args(Namespace):
    demo: DemoArg


class DemoArg(StrEnum):
    KITCHEN_SINK = "kitchensink"


def main() -> None:
    # create argparser
    parser = ArgumentParser(
        prog="axonkit",
        description="Demos of Axon UI + Axon UI Component Kit.",
    )
    parser.add_argument(
        "-d",
        "--demo",
        type=DemoArg,
        default=DemoArg.KITCHEN_SINK,
        choices=list(DemoArg),
        help="demo to run",
        dest="demo",
    )

    # parse arguments
    args: Args = parser.parse_args(namespace=Args())

    # local imports after reading arguments
    import axon

    # relative imports
    from ._demos import KitchenSinkApp

    # create app
    app: axon.App[Any]
    match args.demo:
        case DemoArg.KITCHEN_SINK:
            app = KitchenSinkApp()

    # run app
    app.run()


if __name__ == "__main__":
    main()
