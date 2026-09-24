#!/usr/bin/env python3

import sys
import pygame
from typing import Optional
from fly_parser import parser_file, ParseError
from baseclasses import Set_Up
from scheduler import Schedule
from display import Display

DEFAULT_MAP = "01_the_impossible_dream.txt"


def load_setup(map_file: str) -> Optional[Set_Up]:
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

    map_file = "maps/challenger/01_the_impossible_dream.txt"

    pygame.init()
    surface = pygame.display.set_mode((1920, 1080))
    setup = load_setup(map_file)
    if setup is None:
        return 1
    dsp = Display()
    try:
        dsp.start_display(setup=setup,
                          disp_surface=surface)
    except KeyboardInterrupt:
        pygame.quit()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
