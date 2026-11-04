# Manual fork assignment — 2026-11-04

## Goal and decision

Test scheduling across two routes before changing route discovery. The fork
has two equal-length branches. D1 and D3 were assigned `path_a`; D2 and D4
were assigned `path_b` in a test.

`Simulator.traverse_routes()` now accepts a route for every drone ID. It
validates the assignments and route steps, then runs the existing four-stage
turn loop. Each drone proposes from its own route; all proposals share the
same hub, connection, and restricted-arrival capacity check. The original
`traverse(path)` remains a convenience entry point that assigns one route to
every drone, so the CLI behavior is unchanged.

## Evidence

The fork test produced four turns:

```text
D1-junction D2-junction
D1-path_a D2-path_b D3-junction D4-junction
D1-goal D2-goal D3-path_a D4-path_b
D3-goal D4-goal
```

The single-route fork run takes six turns. Tests also check a missing route
assignment, and all earlier simulation tests remain green. Route choice is
still manual; no new pathfinding algorithm was added in this waypoint.

## Next

Find both fork routes automatically, then decide how to assign drones based
on route cost and capacity. Test routes that share or reconverge at a hub.
