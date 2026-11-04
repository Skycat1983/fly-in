# Progress board

Updated 2026-11-04. See the [restart checkpoint](2026-10-29-restart.md) for
the earlier route-finding work and the
[normal-movement checkpoint](2026-11-04-normal-movement.md) for the latest
implementation.

## Current goal

Model **one drone entering a restricted zone over two turns**. On the first
turn, emit the connection name and put the drone in transit. On the next turn,
emit the destination hub and complete arrival without extra waiting.

## Milestones

- [x] Parse and validate maps into typed records.
- [x] Index hubs and connections in `Graph`.
- [x] Find one least-cost route with Dijkstra; return `[]` if unreachable.
- [x] Simulate one drone through normal zones, including CLI movement lines.
- [ ] Handle one drone entering a restricted zone over two turns.
- [ ] Move multiple drones, respecting hub and connection capacities and
      simultaneous moves.
- [ ] Add waiting and route distribution; check for conflicts and deadlocks.
- [ ] Prefer priority zones among suitable equal-cost routes.
- [ ] Complete restricted-movement output and colored visual feedback.
- [ ] Compare turn counts with the supplied map targets.
- [ ] Complete submission README, parser edge cases, docstrings, and lint.

## Open decisions

- Decide how to represent a drone in transit so arrival on the next turn is
  mandatory and destination capacity is reserved in time.
- Decide how route distribution will use the simulator once multiple drones
  are supported. The current simulator rejects maps with more than one drone.

## Logging rule

When a milestone is done or a tricky issue is resolved, add one short dated
file here: **goal → obstacle → decision and reason → evidence → next**. Update
this board at the same time. Combine routine sessions into one milestone log.
