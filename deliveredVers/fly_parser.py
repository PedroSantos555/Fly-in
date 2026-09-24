from typing import Dict, Tuple, Any, List, Set, Optional, cast, Literal
from baseclasses import Set_Up, Hub, Connection
from baseclasses import sprite_hub, Drone, sprite_drone


class ParseError(Exception):
    """Raised when the input map file is invalid."""
    pass


def get_start_end(hubs: Dict[str, Hub]) -> Tuple[Hub, Hub]:
    """Locate the start and end hubs.

    Args:
        hubs: Map of hub name to hub.

    Returns:
        A (start_hub, end_hub) tuple.
    """
    end_hub: Optional[Hub] = None
    start_hub: Optional[Hub] = None

    for _, hub in hubs.items():
        if hub.kind == "end_hub":
            end_hub = hub

        if hub.kind == "start_hub":
            start_hub = hub

    if start_hub is None or end_hub is None:
        raise ParseError(
            "Map must contain exactly one start_hub and one end_hub"
        )
    return start_hub, end_hub


def parse_attributes(raw_attributes: str, nline: int) -> Dict[str, Any]:
    """Parse a metadata block such as 'zone=normal color=red'.

    Args:
        raw_attributes: Text between the brackets.
        nline: Line number, used in error messages.

    Returns:
        Map of attribute name to value.

    Raises:
        ParseError: If an attribute is malformed.
    """

    att_dict: Dict[str, Any] = {}
    for group in raw_attributes.split():
        if "=" not in group:
            raise ParseError(
                f"Line {nline}: Invalid attribute '{group}'"
            )
        total = group.split("=", 1)

        if len(total) != 2:
            raise ParseError(
                f"Line {nline}: Invalid attribute '{group}'"
            )
        name, value = total
        parsed_value: Any = value
        if value == "":
            raise ParseError(
                f"Line {nline}: Invalid attribute '{group}'"
            )
        if name in {"max_drones", "max_link_capacity"}:
            parsed_value = int(value)
        att_dict[name] = parsed_value

    return att_dict


def parser_file(file: str) -> Set_Up:
    """Parse a map file into a simulation setup.

    Args:
        file: Path to the map file.

    Returns:
        The setup with drones, hubs and connections.

    Raises:
        ParseError: If the file content is invalid.
    """

    nb_drones = 0
    drones = []
    hubs = {}
    connections: List[Connection] = []
    coords: Set[Tuple[str, str]] = set()
    endhb = 0
    starthb = 0

    with open(file) as f:
        text = f.read()

    for nline, line in enumerate(text.splitlines(), start=1):

        if not line or line.startswith("#"):
            continue

        elif line.startswith("nb_drones:"):
            _, rest = line.split(":", 1)
            try:
                nb_drones = int(rest.strip())
            except Exception:
                raise ParseError(
                        f"Line {nline}: invalid drone number. "
                        "Must be positive int")
            if nb_drones < 1:
                raise ParseError(
                        f"Line {nline}: number of drones must be 1 or more")

        elif line.startswith(("hub:", "end_hub:", "start_hub:")):
            try:
                rest, attributes = line.split('[', 1)
                kind, info = rest.split(':', 1)
                name, x, y = info.split()
            except ValueError:
                raise ParseError(
                        f"Line {nline}: Hub data '{line}' badly formated"
                        "\n Hub name cant have spaces and must "
                        "have the format 'name: x y [metadata]'")

            if '-' in name:
                raise ParseError(
                        f"Line {nline}: Hub name '{name}' cant have dashes")

            if kind == "end_hub":
                if endhb == 1:
                    raise ParseError(
                        f"Line {nline}: duplicate end_hub '{name}'")
                endhb = 1

            if kind == "start_hub":
                if starthb == 1:
                    raise ParseError(
                        f"Line {nline}: duplicate start_hub '{name}'")
                starthb = 1

            pos = (x, y)
            if pos in coords:
                raise ParseError(
                    f"Line {nline}: duplicate hub coordinates '{name}'")
            coords.add(pos)

            if name in hubs:
                raise ParseError(f"Line {nline}: duplicate hub name'{name}'")

            att_dict = parse_attributes(attributes.rstrip("]").strip(), nline)

            try:
                hub_kind = cast(Literal["start_hub", "end_hub", "hub"], kind)
                hubs[name] = Hub(kind=hub_kind,
                                 name=name,
                                 x=int(x),
                                 y=int(y),
                                 color=att_dict.get("color", "none"),
                                 max_drones=att_dict.get("max_drones", 1),
                                 drones_landed=[],
                                 status=att_dict.get("zone", "normal"),
                                 conects=[],
                                 sprite=sprite_hub(int(x), int(y),
                                                   att_dict.get("color",
                                                                "none"),
                                                   att_dict.get("zone",
                                                                "normal")),
                                 reserve_timetable=dict()
                                 )
            except Exception as error:
                raise ParseError(
                    f"Line {nline}: invalid hub '{name}' - {error}")

        elif line.startswith("connection:"):
            _, data = line.split(":", 1)

            if "[" in line:
                paths, attributes = data.split("[")
                att_dict = parse_attributes(attributes.rstrip("]").strip(),
                                            nline)
            else:
                paths = data
                att_dict = {}
            start, end = paths.strip().split("-")

            for cnctn in connections:
                if start == cnctn.start and end == cnctn.end:
                    raise ParseError(
                        f"Line {nline}:"
                        f"Duplicate connection '{start} - {end}'")

                if start == cnctn.end and end == cnctn.start:
                    raise ParseError(
                        f"Line {nline}:"
                        f"Duplicate connection '{start} - {end}'")

            if start not in hubs or end not in hubs:
                raise ParseError(
                    f"Line {nline}:"
                    f"Connection between invalid hubs "
                    f"'{start} - {end}'")

            if att_dict.get("max_link_capacity", 1) < 1:
                raise ParseError(
                    f"Line {nline}:"
                    f"Max number of links must be positive int '{line}'")

            try:
                new_cnct = Connection(start=start, end=end,
                                      max_links=att_dict.get(
                                          "max_link_capacity", 1),
                                      reserve_timetable=dict())
            except Exception:
                raise ParseError(
                    f"Line {nline}: {line}"
                    f"Invalid connection syntax")

            connections.append(new_cnct)

    nid = 1

    starthub, _ = get_start_end(hubs)

    while nb_drones > 0:
        new_drone = Drone(id=nid,
                          position=starthub,
                          sprite=sprite_drone(starthub.x,
                                              starthub.y),
                          script=dict())
        nid += 1
        drones.append(new_drone)
        starthub.drones_landed.append(new_drone)
        nb_drones -= 1

    setup = Set_Up(drones=drones, hubs=hubs, connections=connections)
    setup.structure_connections()
    return setup


if __name__ == "__main__":
    setup = parser_file("03_basic_capacity.txt")
    print(setup)
