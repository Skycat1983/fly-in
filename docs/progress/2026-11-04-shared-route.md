# Shared-route checkpoint — 2026-11-04

## Goal and decision

Move several drones along one route while respecting hub and connection
capacities. Evaluating and applying one drone at a time would make the result
depend on update order. `MoveProposal` therefore records a possible move
without changing the drone.

Each turn has four steps: propose from the turn-start state, choose a set that
fits capacities, apply those moves together, then format one output line.
Required restricted arrivals are chosen first. Other drones are considered
furthest along the route first, so leaving a hub frees it for a follower that
same turn. A drone entering restricted transit reserves one destination slot
for its mandatory next-turn arrival. Connection use is counted for every
accepted move, including an arrival from transit.

## Evidence

`python3 main.py maps/easy/01_linear_path.txt` prints:

```text
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

Tests cover this four-turn schedule, capacity-two hubs and links, and two
drones sharing a restricted route. All 27 tests and lint pass. A smoke run of
the ten supplied maps completed on the single-route scheduler; those turn
counts are not yet a substitute for independent schedule validation.

## Next

First, test route assignment without changing Dijkstra. Give D1 and D3
`start → junction → path_a → goal`; give D2 and D4 the matching `path_b`
route. Change the simulator to read each drone's assigned route while keeping
the existing shared-route entry point. The same capacity check must select
moves from all four drones together. Expected output:

```text
D1-junction D2-junction
D1-path_a D2-path_b D3-junction D4-junction
D1-goal D2-goal D3-path_a D4-path_b
D3-goal D4-goal
```

This isolates scheduling from route discovery. It should improve the fork
from six turns on one route to four turns across two routes. After that passes,
find candidate routes automatically, then choose assignments by expected
fleet completion time. Recheck capacity when routes meet at a hub or link.
