# Progress board

Updated 2026-11-04. See the [restart checkpoint](2026-10-29-restart.md),
[normal-movement checkpoint](2026-11-04-normal-movement.md), and
[restricted-transit checkpoint](2026-11-04-restricted-transit.md). The recent
milestones are [shared-route scheduling](2026-11-04-shared-route.md) and
[manual fork assignment](2026-11-04-manual-fork.md). The latest checkpoint is
[automatic assignment](2026-11-04-automatic-assignment.md), following
[candidate-route discovery](2026-11-04-candidate-routes.md).

## Current goal

Validate generated schedules independently on the supplied maps, then improve
route choice where the current two-plan policy leaves avoidable delays. The
simple fork now completes in four turns through the CLI.

## Milestones

- [x] Parse and validate maps into typed records.
- [x] Index hubs and connections in `Graph`.
- [x] Find one least-cost route with Dijkstra; return `[]` if unreachable.
- [x] Simulate one drone through normal zones, including CLI movement lines.
- [x] Handle one drone entering a restricted zone over two turns.
- [x] Move multiple drones along one route.
- [x] Enforce hub and connection capacities with simultaneous moves.
- [x] Wait on capacity conflicts and report a turn with no possible move.
- [x] Schedule manually assigned routes on the simple fork in four turns.
- [x] Discover alternative route candidates on the simple fork.
- [x] Assign drones to candidate routes automatically with a two-plan trial.
- [ ] Independently validate generated schedules on supplied maps.
- [ ] Prefer priority zones among suitable equal-cost routes.
- [ ] Add colored visual feedback.
- [ ] Compare turn counts with the supplied map targets.
- [ ] Complete submission README, parser edge cases, docstrings, and lint.

## Open decisions

- Check whether excluding one best-route connection finds enough candidates
  on harder maps; it does not enumerate all alternatives.
- Decide how to improve assignment beyond a shared plan and one round-robin
  spread, especially where routes share bottlenecks.
- Decide whether a future multi-route scheduler needs a more general move
  selector than the current one-route, furthest-first order.

## Logging rule

When a milestone is done or a tricky issue is resolved, add one short dated
file here: **goal → obstacle → decision and reason → evidence → next**. Update
this board at the same time. Combine routine sessions into one milestone log.
