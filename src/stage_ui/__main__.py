# std
from argparse import ArgumentParser
from importlib.resources import files
from pathlib import Path
from typing import Any, Literal


def main() -> None:
    # create argparser
    parser = ArgumentParser(
        prog="stage-ui",
        description="",
    )
    parser.add_argument(
        "-d",
        "--data-dir",
        type=Path,
        help="directory to write data files to",
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
        choices=["pandas", "mock"],
        help="backend for writing data",
        dest="data_backend",
    )

    # parse arguments
    args = parser.parse_args()
    data_dir: Path | None = args.data_dir
    camera_index: int | None = args.camera_index
    arduino_backend: Literal["pyserial", "mock"] = args.arduino_backend
    camera_backend: Literal["cv2", "mock"] = args.camera_backend
    data_backend: Literal["pandas", "mock"] = args.data_backend

    # build up configs's kwargs
    cfg_kwargs: dict[str, Any] = {}
    if data_dir is not None:
        cfg_kwargs["DATA_DIR"] = data_dir
    if camera_index is not None:
        cfg_kwargs["DEFAULT_CAMERA_INDEX"] = camera_index

    # local imports after reading arguments
    import stage_ui
    from stage_ui.app import App
    from stage_ui.app_config import AppConfig
    from stage_ui.manager_arduino import MockArduinoManager, PySerialArduinoManager
    from stage_ui.manager_camera import CV2CameraManager, MockCameraManager
    from stage_ui.manager_data import MockDataManager, PandasDataManager

    # print startup info
    ascii_art = (files("stage_ui.resources") / "title.txt").read_text()
    print(f"{ascii_art}\nStageUI: starting v{stage_ui.VERSION}")

    # create config
    cfg = AppConfig(**cfg_kwargs)

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
    data_man = MockDataManager() if data_backend == "mock" else PandasDataManager()
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
