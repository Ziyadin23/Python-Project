"""Application entry point for the Student Database System."""

from __future__ import annotations

import argparse

from student_database.constants import DEFAULT_DATA_PATH


def parse_args() -> argparse.Namespace:
    """Parse command-line options for launching the app."""
    parser = argparse.ArgumentParser(description="Student Database System")
    parser.add_argument(
        "--gui",
        "--web",
        action="store_true",
        help="launch the browser interface",
    )
    parser.add_argument(
        "--data-path",
        default=DEFAULT_DATA_PATH,
        help=f"path to the JSON data file (default: {DEFAULT_DATA_PATH})",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="host for the browser interface (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="port for the browser interface (default: 8000)",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="open the browser interface automatically",
    )
    return parser.parse_args()


def main() -> None:
    """Run either the CLI or the graphical interface."""
    args = parse_args()
    if args.gui:
        from student_database.webapp import run_web_app

        run_web_app(
            data_path=args.data_path,
            host=args.host,
            port=args.port,
            open_browser=args.open_browser,
        )
        return

    from student_database.cli import run_cli

    run_cli(args.data_path)


if __name__ == "__main__":
    main()
