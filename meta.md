# How the program runs

Current behavior, using `make run` (equivalent to
`python3 main.py maps/easy/01_linear_path.txt`). This page follows execution
order. For goals and history, see [progress](docs/progress/README.md).

## From input to route

1. **`main.py` receives a map path.** It requires exactly one command-line
   argument. A missing or extra argument prints usage and exits with code 2.
2. **`InputParser.parse()` reads the file.** It ignores comments and blank
   lines, turns records into typed hubs and connections, validates the map,
   and returns a `MapDefinition`. File or format errors print to stderr and
   exit with code 1.
3. **`Graph(map_data)` indexes the map.** Hub names point to `Hub` objects;
   each connection is available from either endpoint. This is the topology
   used for route lookup.
4. **`RouteFinder(graph).find_candidate_paths()` plans routes.** Dijkstra's
   algorithm explores hubs by lowest known cost. Entering a normal or
   priority hub costs 1 turn; restricted costs 2; blocked hubs are skipped.
   Predecessor links reconstruct the best route. The finder retries with one
   connection of that route excluded to collect alternatives. It returns an
   empty candidate list if the end cannot be reached.

## From route to output

5. **`FleetPlanner.choose_schedule(candidates)` tries two plans.** One puts
   every drone on the best route; the other spreads drones across candidates
   in order. Each plan is simulated separately. The planner keeps the valid
   result with fewer turns, using the shared plan on a tie.
6. **`Simulator` in `simulator.py` creates the drones.**
   Every drone starts at the start `Hub` with `route_index = 0`. An empty
   route produces an error. `traverse()` accepts one shared route;
   `traverse_routes()` accepts a route assigned to each drone.
7. **One loop iteration schedules one turn, in four steps:**
   1. Each undelivered drone proposes its next move on its assigned route
      without changing state.
   2. The simulator chooses moves that fit hub and connection capacities. It
      handles required restricted arrivals first, then drones furthest along
      the route. Departures free hub space for arrivals in the same turn.
   3. It applies all accepted moves together. Rejected proposals wait.
   4. It adds 1 to `turn_counter` and formats one line containing the accepted
      movements in drone-ID order. Waiting drones are omitted.
8. **Delivery ends the loop.** When every drone is at the last route entry,
   there are no proposals. The simulator returns its lines; `main()` prints
   them and exits with code 0. A turn with no accepted move reports an error.

For the default two-drone map, each turn ends in these positions:

| Turn | D1 | D2 | Output line |
| ---: | --- | --- | --- |
| Start | `start` | `start` | — |
| 1 | `waypoint1` | `start` | `D1-waypoint1` |
| 2 | `waypoint2` | `waypoint1` | `D1-waypoint2 D2-waypoint1` |
| 3 | `goal` | `waypoint2` | `D1-goal D2-waypoint2` |
| 4 | `goal` | `goal` | `D2-goal` |

For `examples/one_drone_restricted.txt`, the turn lines are
`D1-start-restricted`, `D1-restricted`, and `D1-goal`. During the first turn,
the drone's `location` is the connection and its route index still points to
`start`. Its destination hub is reserved so arrival can happen on the next
turn.

**Current boundary:** assignment compares only two plans: everyone on the
best route, or one round-robin spread. Candidate discovery is limited to
excluding one best-route connection at a time. Priority preference and
colored output are future work.
