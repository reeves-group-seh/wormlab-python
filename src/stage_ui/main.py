# item imports
from argparse import ArgumentParser
from pathlib import Path

# local item imports
from app import App

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
        "-c",
        "--camera-index",
        help="the OpenCV video capture camera index",
        type=int,
    )
    parser.add_argument(
        "-o",
        "--data-dir",
        help="the directory to write the datafile to",
        type=Path,
    )

    # parse arguments
    args = parser.parse_args()

    # create & run app
    app = App.new(
        testing=args.testing,
        data_dir=args.data_dir,
        camera_index=args.camera_index,
    )
    app.run()
