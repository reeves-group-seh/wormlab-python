# std
from argparse import ArgumentParser
from importlib.metadata import version
from importlib.resources import files
from pathlib import Path
from typing import Literal

from stage_ui.manager_arduino import PySerialArduinoManager
from stage_ui.manager_camera import MockCameraManager
from stage_ui.manager_data import PandasDataManager


def main() -> None:
    # create argparser
    parser = ArgumentParser(
        prog="stage_ui",
        description="",
    )
    parser.add_argument(
        "-d",
        "--data-dir",
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
        "--arduino-backend",
        default="pyserial",
        choices=["pyserial", "mock"],
        help="backend for serial communication with the arduino",
        dest="arduino_backend",
    )
    parser.add_argument(
        "--camera-backend",
        default="cv2",
        choices=["cv2", "mock"],
        help="backend for the camera",
        dest="camera_backend",
    )
    parser.add_argument(
        "--data-backend",
        default="pandas",
        choices=["pandas"],
        help="backend for writing data",
        dest="data_backend",
    )

    # parse arguments
    args = parser.parse_args()
    data_dir: Path | None = args.data_dir
    camera_index: int | None = args.camera_index
    arduino_backend: Literal["pyserial", "mock"] = args.arduino_backend
    camera_backend: Literal["cv2", "mock"] = args.camera_backend
    data_backend: Literal["pandas"] = args.data_backend

    # local imports after reading arguments

    from stage_ui.app import App
    from stage_ui.config import Config
    from stage_ui.manager_arduino import MockArduinoManager
    from stage_ui.manager_camera import CV2CameraManager

    # print startup info
    ascii_art = (files("stage_ui.resources") / "title.txt").read_text()
    print(f"{ascii_art}\nStageUI: starting v{version('stage-ui')}")

    # create config
    cfg = Config(
        data_dir=data_dir,
        camera_index=camera_index,
    )

    # create & run app
    arduino_man = (
        MockArduinoManager()
        if arduino_backend == "mock"
        else PySerialArduinoManager(
            baudrate=cfg.SERIAL_BAUDRATE,
            timeout=cfg.SERIAL_TIMEOUT,
            sleep_factor=cfg.SERIAL_SLEEP_FACTOR,
        )
    )
    camera_man = MockCameraManager() if camera_backend == "mock" else CV2CameraManager()
    data_man = PandasDataManager()
    data_man.open(cfg.DATA_FILE)
    app = App(
        cfg,
        arduino_man=arduino_man,
        camera_man=camera_man,
        data_man=data_man,
    )
    app.run()


if __name__ == "__main__":
    main()
