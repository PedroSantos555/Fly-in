# Implement Djikstra algoythm with aditional weights for queue length,
# hub/line utilization, and expected wait time!
from baseclasses import Hub, Set_Up, Connection
from typing import Dict, Tuple, Optional, List
import heapq


def waiting_time(timetable: Dict[int, int], max_drones: int,
                 arrival_time: int) -> int:
    """Find how long to wait for a free slot.

    Args:
        timetable: Map of turn to number of reservations.
        max_drones: Capacity of the hub or connection.
        arrival_time: Turn at which the drone arrives.

    Returns:
        Number of turns to wait until capacity is available.
    """
    # this seems both too simple, and like itll work?

    i = round(arrival_time)

    while timetable.get(i, 0) >= max_drones:
        i += 1

    return (i - arrival_time)


def find_connection(hub1: Hub, hub2: Hub) -> Optional[Connection]:
    """Find the connection linking two hubs.

    Args:
        hub1: First hub.
        hub2: Second hub.

    Returns:
        The connection, or None if the hubs are not linked.
    """
    for connect in hub1.conects:
        if connect.end == hub2.name or connect.start == hub2.name:
            return connect
    return None


def weight(start_hub: Hub, end_hub: Hub, time: int) -> float:
    """Compute the cost of moving between two adjacent hubs.

    Combines the zone type cost with the expected waiting time
    on the connection and the destination hub.

    Args:
        start_hub: Hub the drone leaves.
        end_hub: Hub the drone enters.
        time: Turn at which the move would start.

    Returns:
        The move cost, or infinity if the destination is blocked.
    """
    # will have to drastically improved!!
    # Tip 1 - add weight based on expected wait time on path,
    # which we calculate with the schedule
    # (have to look up the next time there's a free spot, and use that)!

    weight = 0
    wait_time = 0
    connection = find_connection(start_hub, end_hub)

    if connection is not None and connection.max_links <= connection.reserve_timetable.get(time, 0):

        wait_time += waiting_time(connection.reserve_timetable,
                                  connection.max_links, time)
        time += wait_time

    if end_hub.status == "blocked":
        return float('inf')

    if end_hub.max_drones <= end_hub.reserve_timetable.get(time, 0):

        wait_time += waiting_time(end_hub.reserve_timetable,
                                  end_hub.max_drones, time)

    if end_hub.status == "priority":
        weight += 0.99

    elif end_hub.status == "normal":
        weight += 1

    elif end_hub.status == "restricted":
        weight += 2

    return weight + wait_time


def get_start_end(hubs: Dict[str, Hub]) -> Tuple[Hub, Hub]:
    """Locate the start and end hubs.

    Args:
        hubs: Map of hub name to hub.

    Returns:
        A (start_hub, end_hub) tuple.
    """
    end_hub = None
    start_hub = None

    for _, hub in hubs.items():
        if hub.kind == "end_hub":
            end_hub = hub

        if hub.kind == "start_hub":
            start_hub = hub

    return start_hub, end_hub


def shortest_path_calc(hubs: Dict[str, Hub],
                       start: Hub) -> Tuple[Dict[str, float],
                                            Dict[str, Optional[str]]]:
    """Run a weighted Dijkstra search from a hub.

    Args:
        hubs: Map of hub name to hub.
        start: Hub to search from.

    Returns:
        A tuple (distance, previous) of dictionaries keyed by hub
        name, used to rebuild paths.
    """

    # have to figure a way to implement time tracking for scheduling 
    # so far trying with distance as proxy

    # have to implement waiting! maybe not here BUT SOMEWHERE 
    # MAYBE I convert the path+timetble into a proper schedule drones follow each turn
    # OR MAYBE - I SEARCH IN THE TIME DIMENSION AS WELL AS THE SPACE DIMENSION 
    # AND GIVE THIS ALGO AN EXTRA DIMENSION

    distance = {hub: float('inf') for hub in hubs}
    previous = {hub: None for hub in hubs}
    distance[start.name] = 0
    neighbors = []
    prio_q = []
    heapq.heappush(prio_q, (distance[start.name], start.name))

    while (prio_q):  # search continues while unvisited neighbors exist
        dist, current = heapq.heappop(prio_q)
        neighbors = []
        if dist > distance[current]:  # skips outdated duplicates in heap
            continue

        for connection in hubs[current].conects:
            if connection.start == current:
                neighbors.append(connection.end)
            elif connection.end == current:
                neighbors.append(connection.start)

        #print(f"neighboorhood of {current}: {neighbors}")

        for close_hub in neighbors:

            new_distance = distance[current] + weight(hubs[current],
                                                      hubs[close_hub],
                                                      round(distance[current]
                                                            + 1))
            # print("time used", distance[current] + 1)

            if new_distance <= distance[close_hub]:
                distance[close_hub] = new_distance
                previous[close_hub] = current
                heapq.heappush(prio_q, (distance[close_hub], close_hub))

    return distance, previous


def reconstruct_path(previous: Dict[str, Optional[str]],
                     start: str, end: str) -> List[str]:
    """Rebuild the path from start to end.

    Args:
        previous: Predecessor map from the search.
        start: Name of the start hub.
        end: Name of the end hub.

    Returns:
        Ordered list of hub names, or an empty list if unreachable.
    """
    path = []
    current = end

    while current is not None:

        path.append(current)
        current = previous[current]

    path.reverse()

    if path[0] != start:
        return []
    return path


class Schedule():
    """Assigns each drone a path and a turn-by-turn script."""

    def __init__(self, setup: Set_Up) -> None:
        """Store the setup to schedule.

        Args:
            setup: Parsed simulation setup.
        """
        self.setup = setup
        self.hubs = setup.hubs
        self.drones = setup.drones

    def schedule_drones(self) -> None:
        """Compute a path for each drone and reserve its slots.

        Fills each drone's script and the hub and connection
        reservation timetables.
        """
        _, end = get_start_end(self.hubs)
        c_finish = 0

        for drone in self.drones:
            distance, prev = shortest_path_calc(self.hubs, drone.position)
            path = reconstruct_path(prev, drone.position.name, end.name)

            turns_wait = 0

            for number, hub in enumerate(path):
                next_hub = self.hubs[hub]
                current_hub = self.hubs["start"]

                if number > 0:
                    current_hub = self.hubs[path[number - 1]]
                    conection = find_connection(current_hub, next_hub)

                    if conection is None:
                        raise ValueError(f"Connection between {current_hub.name} and {next_hub.name} doesnt exist")

                    while conection.max_links <= conection.reserve_timetable.get(number + turns_wait, 0):

                        if not current_hub.reserve_timetable.get(number + turns_wait):
                            current_hub.reserve_timetable[number + turns_wait] = 1
                        else:
                            current_hub.reserve_timetable[number + turns_wait] += 1

                        turns_wait += 1

                    if not conection.reserve_timetable.get(number + turns_wait):
                        conection.reserve_timetable[number + turns_wait] = 1
                    else:
                        conection.reserve_timetable[number + turns_wait] += 1

                if next_hub.kind == "end_hub":
                    c_finish += 1
                    next_hub.reserve_timetable[number + turns_wait] = c_finish
                    drone.script[number + turns_wait] = (next_hub.x, next_hub.y, next_hub.name)
                    continue

                elif next_hub.status == "restricted":
                    turns_wait += 1

                while next_hub.max_drones <= next_hub.reserve_timetable.get(number + turns_wait, 0):
                    if not current_hub.reserve_timetable.get(number + turns_wait):
                        current_hub.reserve_timetable[number + turns_wait] = 1
                    else:
                        current_hub.reserve_timetable[number + turns_wait] += 1
                    turns_wait += 1

                drone.script[number + turns_wait] = (next_hub.x, next_hub.y, next_hub.name)

                if next_hub.status == "restricted":
                    x, y = (current_hub.x + ((next_hub.x - current_hub.x) / 2),
                            (current_hub.y + (next_hub.y - current_hub.y) / 2))

                    cnc_name = f"C[{current_hub.name}-{next_hub.name}]"

                    drone.script[number + turns_wait - 1] = (x, y, cnc_name)

                if not next_hub.reserve_timetable.get(number + turns_wait):
                    next_hub.reserve_timetable[number + turns_wait] = 1
                else:
                    next_hub.reserve_timetable[number + turns_wait] += 1


def end_turn(setup: Set_Up) -> int:
    """Find the turn when all drones have reached the end hub.

    Args:
        setup: Simulation setup after scheduling.

    Returns:
        The final turn number (0 if never reached).
    """
    start, end = get_start_end(setup.hubs)
    endturn = 0
    for nturn, ndrones in end.reserve_timetable.items():
        if ndrones == len(setup.drones):
            endturn = nturn

    return endturn
