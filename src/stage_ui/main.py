# item imports
from argparse import ArgumentParser
from pathlib import Path

# when run as script
if __name__ == "__main__":
    # create argparser
    parser = ArgumentParser(
        prog="stage_ui",
        description="",
    )
    parser.add_argument(
        "--dev",
        help="run the program in developer mode",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--data-dir",
        help="the directory to write the datafile to",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "-c",
        "--camera-index",
        help="the OpenCV video capture camera index",
        type=int,
    )

    # parse arguments
    args = parser.parse_args()

    # unwrap arguments
    dev: bool = args.dev
    data_dir: Path = args.data_dir
    camera_index: int | None = args.camera_index

    # import after parsing cli arguments
    from app import App

    # create & run app
    app = App.new(
        testing=dev,
        data_dir=data_dir,
        camera_index=camera_index,
    )
    app.run()
