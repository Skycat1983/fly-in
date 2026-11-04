# Normal movement checkpoint — 2026-11-04

## Goal

Turn a route into one movement line per turn for a single drone, and stop on
delivery. The walkthrough route is `start → waypoint1 → waypoint2 → goal`.

## Obstacle and decision

The bundled linear map declares two drones. Silently moving only `D1` would
misrepresent that input, so the simulator reports an error for multi-drone
maps until scheduling is implemented. A separate one-drone example in
`examples/` keeps the ten supplied maps intact and makes `make run` useful.

`Drone` owns its current route index and hub location. A normal turn advances
both and returns the destination name. `Simulator` counts turns and formats
that name as `D<ID>-<hub>` through `format_movement()`. It returns the turn
lines for the CLI to print. An empty route reports an error; a restricted
destination raises an explicit unfinished-feature error without moving the
drone.

## Evidence

`make run` prints exactly:

```text
D1-waypoint1
D1-waypoint2
D1-goal
```

The new simulator tests cover the three-turn result, exact CLI output, and
rejection of a two-drone map. The drone test checks each location and route
index, including no further movement after delivery.

## Next

Represent restricted transit explicitly. The source hub becomes free when the
drone enters its connection; the destination hub is occupied on the next
turn. The simulation must reserve that arrival so the drone cannot wait on
the connection.
