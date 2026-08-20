# Implement Djikstra algoythm with aditional weights for queue length,
# hub/line utilization, and expected wait time!
from baseclasses import Hub, Set_Up, Connection
from typing import Dict, Tuple, Optional, List
import heapq

from display import Display, parser_file


def waiting_time(timetable: Dict[int, int], max_drones: int,
                 arrival_time: int) -> int:
    # this seems both too simple, and like itll work?

    i = round(arrival_time)

    while timetable.get(i, 0) >= max_drones:
        i += 1

    return (i)


def find_connection(hub1: Hub, hub2: Hub) -> Optional[Connection]:
    for connect in hub1.conects:
        if connect.end == hub2.name or  connect.start == hub2.name:
            return connect
    return None


def weight(start_hub: Hub, end_hub: Hub, time: int) -> float:
    # will have to drastically improved!!
    # Tip 1 - add weight based on expected wait time on path,
    # which we calculate with the schedule
    # (have to look up the next time there's a free spot, and use that)!

    weight = 0
    wait_time = 0
    connection = find_connection(start_hub, end_hub)

    if connection.max_links <= connection.reserve_timetable.get(time, 0):

        wait_time += waiting_time(connection.reserve_timetable,
                                  connection.max_links, time)
        time += wait_time

    if end_hub.status == "blocked":
        return float('inf')

    if (time < 25):
        print(end_hub.name, "\n", end_hub.reserve_timetable)
        print("TIME CHECKED: ", time)
    if end_hub.max_drones <= end_hub.reserve_timetable.get(time, 0):

        wait_time += waiting_time(end_hub.reserve_timetable,
                                 end_hub.max_drones, time)

    if end_hub.status == "priority":
        weight += 0.99

    elif end_hub.status == "normal":
        weight += 1

    elif end_hub.status == "restricted":
        weight += 2

    connect = find_connection(start_hub, end_hub)

    return weight + wait_time


def get_start_end(hubs: Dict[str, Hub]) -> Tuple[Hub, Hub]:
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

        if dist > distance[current]:  # skips outdated duplicates in heap
            continue

        for connection in hubs[current].conects:
            if connection.start == current:
                neighbors.append(connection.end)
            else:
                neighbors.append(connection.start)

        for close_hub in neighbors:

            new_distance = distance[current] + weight(hubs[current],
                                                      hubs[close_hub],
                                                      round(distance[current] + 1))
            # print("time used", distance[current] + 1)

            if new_distance < distance[close_hub]:
                distance[close_hub] = new_distance
                previous[close_hub] = current
                heapq.heappush(prio_q, (distance[close_hub], close_hub))

    return distance, previous


def reconstruct_path(previous: Dict[str, Optional[str]],
                     start: str, end: str) -> List[str]:
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

    def __init__(self, setup: Set_Up) -> None:
        self.setup = setup
        self.hubs = setup.hubs
        self.drones = setup.drones

    def schedule_drones(self) -> None:
        _, end = get_start_end(self.hubs)

        for drone in self.drones:
            distance, prev = shortest_path_calc(self.hubs, drone.position)
            path = reconstruct_path(prev, drone.position.name, end.name)

            turns_wait = 0

            for number, hub in enumerate(path):
                next_hub = self.hubs[hub]

                if number > 0:

                    conection = find_connection(path[number - 1], next_hub)

                    while conection.max_links <= Connection.reserve_timetable.get(number + turns_wait, 0):
                        turns_wait += 1

                    if not conection.reserve_timetable.get(number + turns_wait):
                        conection.reserve_timetable[number + turns_wait] = 1
                    else:
                        conection.reserve_timetable[number + turns_wait] += 1

                if next_hub.status == "restricted":
                    turns_wait += 1

                while next_hub.max_drones <= next_hub.reserve_timetable.get(number + turns_wait, 0):
                    turns_wait += 1

                if not next_hub.reserve_timetable.get(number + turns_wait):
                    next_hub.reserve_timetable[number + turns_wait] = 1
                else:
                    next_hub.reserve_timetable[number + turns_wait] += 1
        print(distance)

    def execute_turn(self, turn: int) -> None:
        pass


if __name__ == "__main__":
    setup = parser_file("03_basic_capacity.txt")
    # setup = parser_file("01_the_impossible_dream.txt")
    # print(setup)
    dsp = Display()
    # dsp.start_display(setup=setup)
    dist, prev = shortest_path_calc(setup.hubs, setup.hubs["start"])
    schedule = Schedule(setup)
    schedule.schedule_drones()

    for key, value in schedule.hubs.items():
        print(f"{value.name}: {value.reserve_timetable}")
