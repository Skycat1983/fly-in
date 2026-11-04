# Candidate routes — 2026-11-04

## Goal and decision

Find both simple-fork branches automatically without changing the CLI or
simulator. Rerunning Dijkstra on the same graph returns the same best path, so
`RouteFinder.find_candidate_paths()` first finds that path, then reruns the
search while excluding each of its connections in turn. The exclusion is an
undirected pair of hub names. Duplicate results are removed and alternatives
are ordered by travel cost, then name, up to the requested result limit.

The method uses a fresh `RouteFinder` for each retry, so the original
finder's search state still describes the primary route.

## Evidence and limit

The simple fork yields:

```text
start → junction → path_a → goal
start → junction → path_b → goal
```

The linear map yields only its original route. Tests cover both cases,
undirected exclusion, and an invalid result limit. All 33 tests and lint pass.

This is a bounded candidate search: it runs Dijkstra at most once per
connection of the best route, plus the original search. It does not guarantee
all possible routes or the global second through kth shortest paths. That
limit should be reassessed when working on harder maps.

## Next

Assign drones to the discovered candidates, beginning with the fork. Compare
the four-turn split with the six-turn single-route schedule, then decide how
to estimate which assignment finishes the fleet soonest.
