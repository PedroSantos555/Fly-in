#!/usr/bin/env python3
"""Fly-in: entry point for the drone traffic simulation.

Usage:
    python3 main.py <map_file>
"""

import sys
import argparse

import pygame

from fly_parser import parser_file, ParseError
from scheduler import Schedule
from display import Display


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        The parsed arguments, holding the path to the map file.
    """
    parser = argparse.ArgumentParser(
        prog="fly-in",
        description="Simulate drone traffic across a network of hubs."
    )
    parser.add_argument("map_file", help="Path to the map file to load")
    return parser.parse_args()


def load_setup(map_file: str):
    """Parse the map file into a simulation setup and schedule drones.

    Args:
        map_file: Path to the map file.

    Returns:
        The scheduled Set_Up, or None if parsing/reading failed
        (an error has already been printed to stderr).
    """
    try:
        setup = parser_file(map_file)
    except ParseError as error:
        print(f"Error: {error}", file=sys.stderr)
        return None
    except FileNotFoundError:
        print(f"Error: file '{map_file}' not found", file=sys.stderr)
        return None
    except OSError as error:
        print(f"Error: could not read '{map_file}' - {error}", file=sys.stderr)
        return None

    schedule = Schedule(setup)
    schedule.schedule_drones()
    return setup


def main() -> int:
    """Parse a map, schedule the drones and run the display.

    Returns:
        Process exit code (0 on success, 1 on error).
    """
    args = parse_args()

    setup = load_setup(args.map_file)
    if setup is None:
        return 1

    pygame.init()
    pygame.display.set_mode((1920, 1080))

    dsp = Display()
    try:
        dsp.start_display(setup=setup)
    except KeyboardInterrupt:
        pygame.quit()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
