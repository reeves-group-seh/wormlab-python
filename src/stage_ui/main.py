# item imports
from argparse import ArgumentParser
from pathlib import Path

# local item imports
from stage_ui.config import Config


def main() -> None:
    # create argparser
    parser = ArgumentParser(
        prog="stage_ui",
        description="",
    )

    # parse arguments
    args = parser.parse_args()

    # create config
    cfg = Config(
        Path("test.tmp.csv"),
        testing=True,
        camera_index=3,
    )

    # import after parsing cli arguments
    from stage_ui.app import App

    # create & run app
    app = App(cfg)
    app.run()


if __name__ == "__main__":
    main()
