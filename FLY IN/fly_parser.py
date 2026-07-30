from typing import Dict
from baseclasses import Set_Up, Hub, Connection
from baseclasses import sprite_hub, Drone
from baseclasses import sprite_drone


class ParseError(Exception):
    pass


def parse_attributes(raw_attributes: str) -> Dict:

    att_dict = {}
    for group in raw_attributes.split():
        if "=" not in group:
            raise ParseError(
                f"Invalid attribute '{group}'"
            )
        name, value = group.split("=", 1)
        if name in {"max_drones", "max_link_capacity"}:
            value = int(value)
        att_dict[name] = value

    return att_dict


def parser_file(file: str) -> Set_Up:

    nb_drones = 0
    drones = []
    hubs = {}
    connections = []
    with open(file) as f:
        text = f.read()

    for nline, line in enumerate(text.splitlines(), start=1):

        if not line or line.startswith("#"):
            continue

        elif line.startswith("nb_drones:"):
            _, rest = line.split(":", 1)
            nb_drones = int(rest.strip())

        elif line.startswith(("hub:", "end_hub:", "start_hub:")):
            rest, attributes = line.split('[', 1)
            kind, info = rest.split(':', 1)
            name, x, y = info.split()
            if name in hubs:
                raise ParseError(
                    f"Line {nline}: duplicate hub '{name}'")
            att_dict = parse_attributes(attributes.rstrip("]").strip())

            hubs[name] = Hub(kind=kind,
                             name=name,
                             x=int(x),
                             y=int(y),
                             color=att_dict.get("color", "none"),
                             max_drones=att_dict.get("max_drones", 1),
                             drones_landed=[],
                             status=att_dict.get("zone", "normal"),
                             conects=[],
                             sprite=sprite_hub(int(x), int(y)),
                             reserve_timetable=dict()
                             )

        elif line.startswith("connection:"):
            _, data = line.split(":", 1)
            if "[" in line:
                paths, attributes = data.split("[")
                att_dict = parse_attributes(attributes.rstrip("]").strip())
            else:
                paths = data
                att_dict = {}
            start, end = paths.strip().split("-")
            new_cnct = Connection(start=start, end=end,
                                  max_links=att_dict.get("max_link_capacity",
                                                         1))
            connections.append(new_cnct)

    while nb_drones > 0:
        new_drone = Drone.from_hub(hubs["start"])
        drones.append(new_drone)
        hubs[start].drones_landed.append(new_drone)
        nb_drones -= 1

    setup = Set_Up(drones=drones, hubs=hubs, connections=connections)
    setup.structure_connections()
    return setup


if __name__ == "__main__":
    setup = parser_file("03_basic_capacity.txt")
    print(setup)
