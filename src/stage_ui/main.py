# std
from argparse import ArgumentParser
from pathlib import Path


def main() -> None:
    # create argparser
    parser = ArgumentParser(
        prog="stage_ui",
        description="",
    )

    # parse arguments
    args = parser.parse_args()
    print(args)

    # local imports after reading arguments
    from stage_ui.app import App
    from stage_ui.config import Config
    from stage_ui.manager_camera import CV2CameraManager
    from stage_ui.manager_data import DataManager
    from stage_ui.manager_serial import MockSerialManager

    # create config
    cfg = Config(
        Path("test_dir"),
        testing=True,
        camera_index=3,
    )

    # create & run app
    app = App(
        cfg,
        CV2CameraManager(),
        DataManager(_datafile=cfg.DATA_FILE),
        MockSerialManager(),
    )
    app.run()


if __name__ == "__main__":
    main()
