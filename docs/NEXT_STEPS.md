# Fly-In: Next Steps

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
