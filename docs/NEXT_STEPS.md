# Fly-In: Next Steps

## Current checkpoint: one shortest route works

`RouteFinder.find_shortest_path()` now returns a route as hub names in travel
order:

```text
start -> ... -> end
```

The search uses the parsed start and end names rather than assuming they are
called `start` and `goal`. An unreachable destination returns an empty list.
Tests cover forward reconstruction, custom endpoint names, disconnected and
blocked routes, restricted-zone cost, and deterministic equal-cost results.

Before building more features, be able to explain why `previous` points from a
hub toward its predecessor and why the reconstructed list must be reversed.

That reasoning is correct. When Dijkstra finds a cheaper way to reach a hub, it
knows which already-discovered hub it came from, so it can immediately record
that hub as the predecessor. It cannot yet record the final "next" hub because
the cheapest continuation toward the destination has not necessarily been
discovered. The predecessor links therefore form breadcrumbs from the end back
to the start. Following them produces the route backward, so reconstruction
reverses the completed list once.

## Next task: define the boundary around route finding

Keep shortest-path discovery separate from drone simulation and terminal
output. Think about the contract of `RouteFinder.find_shortest_path()`:

- Is an empty list sufficiently clear for an unreachable destination, or will
  callers need a more descriptive result later?
  For the current milestone, an empty list is sufficient. The parser requires
  different start and end hubs, so an empty route cannot also mean "already at
  the destination." The caller can use `if not path` to detect failure. If the
  program later needs to explain *why* routing failed, consider a specific
  exception or a result object containing both the path and failure details.
  Returning `None` would also be valid, but the return annotation would become
  `list[str] | None`, and every caller would need to handle that second type.
  `[]` keeps the interface simpler while failure has only one meaning.
- Which class should translate hub names into `Hub` objects when metadata is
  needed?
  No new class is required yet. Keep the route as `list[str]`; when the future
  simulator needs zone or capacity metadata, it can ask its `Graph` for each
  hub with `graph.get_hub(name)`. This keeps route finding independent from
  simulation state. If those conversions become repetitive, a dedicated
  `Route` value object may become worthwhile later.
- Should movement-cost calculation remain inside `find_shortest_path()`, or
  would a small, named helper make the rule easier to test and explain?
  A helper would isolate the subject's cost rules from Dijkstra's control flow.
  One possible interface is:

  ```python
  def _movement_cost(zone: ZoneKind) -> int | None:
      """Return the entry cost, or ``None`` when the zone is blocked."""
  ```

  Then focused tests could check normal, priority, restricted, and blocked
  zones without constructing an entire graph. Decide whether returning `None`
  for blocked is clearer than handling blocked zones separately before adopting
  this design.
- What docstring should describe the method's return value and unreachable
  behavior?
  For example:

  ```python
  def find_shortest_path(self) -> list[str]:
      """Return the least-cost route from the start hub to the end hub.

      Returns:
          Hub names in travel order, including both endpoints. Returns an
          empty list when no route can reach the end hub.
      """
  ```

Do not add drone positions, occupancy, or turns to `RouteFinder`. Its result is
a plan; a simulator will execute that plan over time.

## Then: simulate one drone on one route

Start with normal zones only. Decide what state is required to answer these
questions on every turn:

<!-- ? is there a reason why we start with normal zones only? -->

- Where is the drone now?
<!-- ? presumably we are going through the route? so it would be the item we are looking at? -->
- Which route position is next?
- Has the drone reached the end?
- What constitutes one successful move?
- Who owns the turn counter?
- Should a waiting drone produce output? The subject says it should not.

Use the PDF output requirement as the boundary: the simulator should produce
movement events, while a formatter should turn those events into strings such
as `D1-waypoint1`. Avoid printing directly from the route finder.

Useful first simulation checks are:

1. One drone traverses the linear map in the expected number of turns.
2. Exactly one movement is emitted for each normal edge.
3. The final movement names the actual end hub.
4. The simulation stops immediately after delivery.
5. Waiting produces no movement token.

## After normal movement: restricted-zone transit

Entering a restricted zone costs two turns. The PDF distinguishes being in
flight on a connection from occupying the destination zone. Before coding,
write down the state transitions for both turns and consider:

- When does the source zone become free?
- What identifies the occupied connection while the drone is in flight?
- What should be printed on the transit turn?
- When is the restricted destination considered occupied?
- How will the simulator guarantee arrival on the next turn rather than allow
  extra waiting on the connection?

Test this behavior with one drone before introducing any capacity competition.

## Path-selection questions to revisit

Normal and priority zones both cost one turn, but the subject says priority
zones should be preferred. The current heap gives equal-distance entries a
stable order based on hub name. Consider what an explicit priority tie-break
means and how it can be represented without changing the true movement cost.

Also check these cases before relying on one shortest route as a foundation:

- A cheaper route discovered after a more expensive candidate was queued.
- A blocked hub surrounded by otherwise valid connections.
- Multiple equal-cost routes inserted in different connection orders.
- Repeated calls to `find_shortest_path()` on the same `RouteFinder` instance.
- A map whose end hub has a name other than `goal`.

## Later milestones, in order

Only after the one-drone simulator handles normal and restricted movement:

1. Move several drones along one route.
2. Enforce each hub's `max_drones` capacity.
3. Enforce each connection's `max_link_capacity`.
4. Calculate all proposed moves before applying any of them so movement is
   simultaneous and zones vacated that turn free their capacity correctly.
5. Add waiting decisions and tests for conflicts.
6. Find alternative routes and distribute drones between them.
7. Measure turn counts against the easy-map targets before proceeding to the
   medium and hard maps.

For each milestone, separate three questions: is the route valid, is the
turn-by-turn schedule valid, and is the schedule efficient? Solving them all at
once will make failures difficult to diagnose.

## What is complete

- `InputParser` turns a map file into a validated `MapDefinition`.
- `Graph` now lives in `graph.py`.
- `Graph` indexes hubs by name and stores every connection in both directions.
- `Graph.get_hub()`, `Graph.get_neighbours()`, and
  `Graph.get_connection()` provide the topology lookups needed by pathfinding.

Do not add drone scheduling to `Graph`. Its responsibility is only to describe
which hubs exist and how they are connected.

## Understanding `current_name`

`current_name` is not supplied automatically by Python or by `Graph`. It is a
variable a pathfinding algorithm uses to remember which hub it is currently
examining.

For a direct experiment with the simple-fork map, it can be assigned manually:

```python
map_data = InputParser(Path("maps/easy/02_simple_fork.txt")).parse()
graph = Graph(map_data)

current_name = "junction"

for neighbour in graph.get_neighbours(current_name):
    print(neighbour.name)
```

The expected names are `start`, `path_a`, and `path_b`. Using the literal name
directly is also valid:

```python
neighbours = graph.get_neighbours("junction")
```

Later, Dijkstra's algorithm will repeatedly change `current_name` as it removes
the next cheapest hub from its frontier.

## Completed checkpoint: test `Graph`

`tests/test_graph.py` now verifies that:

1. `get_hub("junction")` returns the expected `Hub`.
2. `get_neighbours("junction")` returns `start`, `path_a`, and `path_b`.
3. A connection can be looked up in both directions.
4. The `start-junction` connection retains its `max_link_capacity` of 2.

These tests establish that later pathfinding problems are not graph-construction
problems. The next checkpoint is the one-drone route finder below.

## First pathfinding milestone: one drone, one route

Create a separate `route_finder.py` containing a `RouteFinder` class. Its first
goal should be to return a sequence of hub names from the start hub to the end
hub. Ignore drone capacity and scheduling for this milestone.

Use Dijkstra's algorithm because entering different zone types can have
different costs:

- normal: 1 turn
- priority: 1 turn
- restricted: 2 turns
- blocked: cannot be entered

Coordinates, including negative coordinates, are only for visual placement.
They are not pathfinding costs.

Dijkstra's algorithm will need these pieces of state:

```python
distances: dict[str, int]
previous: dict[str, str | None]
visited: set[str]
```

It will also need a priority queue from Python's `heapq` module. Using `heapq`
is allowed because it is a general-purpose data structure, not a graph library.

For each neighbor of the current hub:

1. Skip it if its zone is blocked.
2. Calculate the cost of entering it.
3. Update its distance and predecessor if the new route is cheaper.
4. Reconstruct the route by following `previous` backward from the end.

Begin with `maps/easy/01_linear_path.txt`. The expected route is:

```text
start -> waypoint1 -> waypoint2 -> goal
```

Then try the simple-fork map. Treat priority as a tie-breaker between routes of
equal cost; it is not a negative movement cost.

## After one route works

Proceed in this order:

1. Simulate one drone moving one normal edge per turn.
2. Add two-turn transit when the destination is restricted.
3. Move several drones along one route.
4. Enforce hub capacity.
5. Enforce connection capacity.
6. Calculate all proposed moves before applying them, because moves in a turn
   happen simultaneously.
7. Find alternative routes and distribute drones between them.
8. Add priority-zone tie-breaking and colored terminal output.
9. Measure the result against the easy-map turn targets before trying harder
   maps.

Do not work on optimal multi-drone scheduling, A*, deadlock optimization, or the
challenger map until the one-drone route finder and simulator are covered by
tests.
