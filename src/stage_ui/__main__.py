# std
from argparse import ArgumentParser, Namespace
from enum import StrEnum
from importlib.resources import files
from pathlib import Path
from typing import Any


class Args(Namespace):
    data_dir: Path | None
    camera_index: int | None
    arduino_backend: ArduinoBackendArg
    camera_backend: CameraBackendArg
    data_backend: DataBackendArg


class ArduinoBackendArg(StrEnum):
    PYSERIAL = "pyserial"
    MOCK = "mock"


class CameraBackendArg(StrEnum):
    CV2 = "cv2"
    MOCK = "mock"


class DataBackendArg(StrEnum):
    PANDAS = "pandas"
    MOCK = "mock"


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
        type=ArduinoBackendArg,
        default=ArduinoBackendArg.PYSERIAL,
        choices=list(ArduinoBackendArg),
        help="backend for serial communication with the arduino",
        dest="arduino_backend",
    )
    parser.add_argument(
        "--camera-backend",
        type=CameraBackendArg,
        default=CameraBackendArg.CV2,
        choices=list(CameraBackendArg),
        help="backend for the camera",
        dest="camera_backend",
    )
    parser.add_argument(
        "--data-backend",
        type=DataBackendArg,
        default=DataBackendArg.PANDAS,
        choices=list(DataBackendArg),
        help="backend for writing data",
        dest="data_backend",
    )

    # parse arguments
    args: Args = parser.parse_args(namespace=Args())

    # local imports after reading arguments
    import stage_ui
    from stage_ui.app import App
    from stage_ui.app_config import AppConfig
    from stage_ui.backend_arduino import (
        ArduinoBackend,
        MockArduinoBackend,
        PySerialArduinoBackend,
    )
    from stage_ui.backend_camera import (
        CameraBackend,
        CV2CameraBackend,
        MockCameraBackend,
    )
    from stage_ui.backend_data import DataBackend, MockDataBackend, PandasDataBackend

    # print startup info
    ascii_art = (files("stage_ui.resources") / "title.txt").read_text()
    print(f"{ascii_art}\nStageUI: starting v{stage_ui.VERSION}")

    # create config
    cfg_kwargs: dict[str, Any] = {}
    if args.data_dir is not None:
        cfg_kwargs["DATA_DIR"] = args.data_dir
    if args.camera_index is not None:
        cfg_kwargs["DEFAULT_CAMERA_INDEX"] = args.camera_index
    cfg = AppConfig(**cfg_kwargs)

    # create arduino backend
    arduino: ArduinoBackend
    match args.arduino_backend:
        case ArduinoBackendArg.PYSERIAL:
            arduino = PySerialArduinoBackend(
                baudrate=cfg.SERIAL_BAUDRATE,
                timeout=cfg.SERIAL_TIMEOUT,
                sleep_factor=cfg.SERIAL_SLEEP_FACTOR,
            )
        case ArduinoBackendArg.MOCK:
            arduino = MockArduinoBackend()

    # create camera backend
    camera: CameraBackend
    match args.camera_backend:
        case CameraBackendArg.CV2:
            camera = CV2CameraBackend()
        case CameraBackendArg.MOCK:
            camera = MockCameraBackend()

    # create data backend
    data: DataBackend
    match args.data_backend:
        case DataBackendArg.PANDAS:
            data = PandasDataBackend()
        case DataBackendArg.MOCK:
            data = MockDataBackend()
    data.open(cfg.DATA_FILE)

    # create & run app
    app = App(
        cfg=cfg,
        arduino=arduino,
        camera=camera,
        data=data,
    )
    app.run()


if __name__ == "__main__":
    main()
