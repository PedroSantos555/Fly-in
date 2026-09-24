*This project has been created as part of the 42 curriculum by <pcoelho->*

# Fly-in

## Description

**Fly-in** routes a fleet of drones from a start zone to an end zone through a network of connected zones, in as few simulation turns as possible.

The network is read from a map file. Each zone has a type that changes its movement cost and a capacity (`max_drones`). Each connection has its own capacity (`max_link_capacity`). The program:

1. **Parses** the map file and validates it (`fly_parser.py`).
2. **Plans** a path and a turn-by-turn script for every drone (`scheduler.py`).
3. **Simulates and displays** the result in a graphical window and prints the moves to the terminal (`display.py`).

### Rules implemented

| Zone type    | Cost to enter | Notes                                       |
|--------------|---------------|---------------------------------------------|
| `normal`     | 1 turn        | Default.                                    |
| `priority`   | 1 turn        | Preferred by the pathfinder (cost 0.99).    |
| `restricted` | 2 turns       | The drone is on the connection for a turn.  |
| `blocked`    | -             | Can never be entered.                       |

- A zone holds at most `max_drones` drones (default 1). The start and end zones have no limit.
- A connection carries at most `max_link_capacity` drones at once (default 1).
- Connections are bidirectional.

### Project structure

| File              | Role                                                                                   |
|-------------------|----------------------------------------------------------------------------------------|
| `baseclasses.py`  | Data model: `Hub`, `Connection`, `Drone`, `Set_Up` (pydantic), plus the pygame sprites and `Camera`. |
| `fly_parser.py`   | Map parser (`parser_file`, `parse_attributes`) and `ParseError`.                        |
| `scheduler.py`    | Pathfinding (Dijkstra with dynamic weights) and the `Schedule` class that books slots.  |
| `display.py`      | Pygame visualisation, turn execution and terminal output.                               |
| `main.py`         | Calls the main functions and launches the simulation and display                        |

## Instructions

### Requirements

- Python 3.10 or later
- `pygame` and `pydantic` (no graph library is used; `networkx`, `graphlib` and similar are forbidden by the subject)
- The `assets/` folder with the hub and drone images, in the directory you run from

### Installation

```
make install
```

### Running
```
make run - runs the program
make lint - checks syntax with mypy and flake8
make lint-strict
make clean - cleans temporary files
make fclean - deep clean of temp files, binaries and the environment
make debug - runs in debug mode

Running different maps requires manually changing the path in main.py
```
### Controls

| Key         | Action                                     |
|-------------|--------------------------------------------|
| `M`         | Toggle autoplay (one turn every 1.5 s)     |
| `N`         | Execute the next turn immediately          |
| `P`         | Show or hide the connections               |
| `1` `2` `3` | Zoom: small, medium, large                 |
| Arrow keys  | Pan the camera                             |


## Algorithm and implementation strategy

### Pathfinding

`shortest_path_calc` is a **Dijkstra search** implemented by hand with a binary heap (`heapq`). The edge weight is not fixed: `weight()` combines

- the **zone cost** of the destination (priority 0.99, normal 1, restricted 2, blocked infinite), which makes the search favour priority zones on otherwise equal paths, and
- the **expected waiting time**, computed from the reservation timetables of the connection and the destination zone (`waiting_time`). If a slot is already full at the expected arrival time, the cost grows by the number of turns until it frees up.

Because the weights depend on the bookings made so far, congested routes become more expensive and later drones are pushed towards other paths. This is how drones get distributed across several routes.

### Scheduling

`Schedule.schedule_drones` handles drones **one after another**:

1. Run the weighted Dijkstra from the start and rebuild the path with `reconstruct_path`.
2. Walk the path hub by hub, tracking a running turn counter. If a connection or hub is full at that turn, the drone **waits** in its current hub until there is room. Waiting is also booked in that hub's timetable so the space is not double-counted.
3. For a **restricted** zone, the drone is placed on the connection for one turn (script entry named `C[a-b]`) and must arrive the next turn, as the subject requires.
4. Book the slot in `reserve_timetable` of every connection and hub used. Each drone's `script` maps *turn -> (x, y, name)*.

The end zone is treated as unlimited, and its timetable is used by `end_turn()` to find the turn at which the last drone arrives.

### Complexity

- One search: O((V + E) log V) with the heap.
- The search is recomputed for every drone, so the total is O(D * (V + E) log V) for D drones, plus the cost of the waiting loops. Paths are **not cached**, because the weights change after each booking.
- Memory is O(V + E) for the graph, plus one timetable entry per booked (turn, hub or connection) pair.

### Limitations

- The scheduler is **greedy**: earlier drones get the best slots, and the result is not guaranteed to be the minimum number of turns.
- Benchmark targets from the subject (e.g. 30 turns for *Maze nightmare*) still need to be measured on every map.

## Visual representation

The graphical interface is built with pygame:

- **Colored hubs.** The `color=` metadata recolors the hub image. A zone type selects the sprite (normal, priority, restricted, blocked), so the network is readable at a glance.
- **Animated drones.** Each move is interpolated between two hubs, so you can see which drones move together in a turn.
- **Stacked drones.** When several drones share a position (start, end, or a multi-capacity hub) a counter is drawn instead of hiding them.
- **Turn control.** Autoplay for a full run, or step by step with `N` to inspect a difficult situation.
- **Zoom and pan.** Three zoom levels and arrow-key panning make large maps navigable.
- **Connections overlay.** `P` draws the links between hubs.
- **Terminal output.** Each turn is printed with the moves of that turn.

## Example

### Input (`example.txt`)

```
nb_drones: 2

start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: roof2 6 2 [zone=normal color=blue]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: tunnelB 7 4 [zone=normal color=red]
hub: obstacleX 5 5 [zone=blocked color=gray]
connection: hub-roof1
connection: hub-corridorA
connection: roof1-roof2
connection: roof2-goal
connection: corridorA-tunnelB [max_link_capacity=2]
connection: tunnelB-goal
```

### Output format

Each turn lists the drones that moved, as `D<ID>-<zone>`, or `D<ID>-C[<zone1>-<zone2>]` for a drone in flight towards a restricted zone. Drones that do not move are omitted, and the simulation ends when all drones have reached the goal.

```
D1-corridorA D2-corridorA

D1-tunnelB D2-tunnelB
...
```

### Error handling

Invalid maps stop the program with a message that includes the line number, for example:

```
Line 7: Hub name 'my-hub' cant have dashes
```

## Resources

### References

- Dijkstra's algorithm: [Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- Python `heapq` (priority queue): [docs.python.org](https://docs.python.org/3/library/heapq.html)
- Pygame documentation: [pygame.org/docs](https://www.pygame.org/docs/)

### Use of AI

AI was used for select debugging, learning about the pygame, and helping draft both this read me and function docstrings
