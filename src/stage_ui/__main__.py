# std
from argparse import ArgumentParser
from importlib.metadata import version
from importlib.resources import files
from pathlib import Path

from stage_ui.manager_camera import MockCameraManager


def main() -> None:
    # create argparser
    parser = ArgumentParser(
        prog="stage_ui",
        description="",
    )
    parser.add_argument(
        "-d",
        "--datadir",
        type=Path,
        help="directory to write datafiles to",
        dest="data_dir",
    )
    parser.add_argument(
        "-i",
        "--camera-index",
        type=int,
        help="default camera index",
        dest="camera_index",
    )
    parser.add_argument(
        "--camera-backend",
        default="cv2",
        choices=["cv2", "mock"],
        help="backend for the camera",
        dest="camera_backend",
    )
    # parser.add_argument(
    #     "--serial-backend",
    #     default="pyserial",
    #     choices=["pyserial", "mock"],
    #     help="backend for communication with the arduino",
    #     dest="serial_backend",
    # )

    # parse arguments
    args = parser.parse_args()
    data_dir: Path | None = args.data_dir
    camera_index: int | None = args.camera_index
    camera_backend: str = args.camera_backend
    # serial_backend: str = args.serial_backend

    # local imports after reading arguments

    from stage_ui.app import App
    from stage_ui.config import Config
    from stage_ui.manager_camera import CV2CameraManager
    from stage_ui.manager_data import DataManager
    from stage_ui.manager_serial import MockSerialManager

    # print startup info
    ascii_art = (files("stage_ui.resources") / "title.txt").read_text()
    print(f"{ascii_art}\nStageUI: starting v{version('stage-ui')}")

    # create config
    cfg = Config(
        data_dir=data_dir,
        camera_index=camera_index,
    )

    # create & run app
    camera_man = MockCameraManager() if camera_backend == "mock" else CV2CameraManager()
    data_man = DataManager(_datafile=cfg.DATA_FILE)
    serial_man = MockSerialManager()
    app = App(
        cfg,
        camera_man=camera_man,
        data_man=data_man,
        serial_man=serial_man,
    )
    app.run()


if __name__ == "__main__":
    main()
