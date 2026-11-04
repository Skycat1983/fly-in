# Fly-in documentation

Start with [progress](progress/README.md) to see the current goal. Read the
[checkpoint log](progress/2026-10-29-restart.md) for the evidence and reasoning
behind the handoff. The [subject](../fly-in.pdf) is the source of truth for
requirements; the code and tests show what is actually implemented.

## How to keep these notes useful

- Keep `progress/README.md` short: current goal, completed milestones, next
  milestones, and unresolved questions only.
- Add one dated checkpoint after a meaningful milestone or a problem worth
  remembering. Record the problem, decision, reason, evidence, and next step.
  Do not create a file for every work session.
- Update the progress board when a milestone changes. Put detailed reasoning
  in the checkpoint, not in the board.
- Use Git history for obsolete drafts. The removed notes remain available in
  earlier commits; they do not need to remain active documentation.
- The required root `README.md` is still to be written before submission. It
  needs setup, example input/output, algorithm, visualization, resources, and
  AI-use disclosure as specified in the subject.

## Project mental model

`InputParser` reads and validates a map; `Graph` indexes its hubs and
connections; `RouteFinder` returns a route as hub names; the future simulator
must turn routes into movements over time. The route is a *plan*, not a schedule.

A hub is a graph vertex and a connection is a bidirectional edge. The current
route cost is the cost of **entering the destination hub**: normal and priority
cost 1 turn, restricted costs 2, and blocked cannot be entered. Coordinates
(including negative coordinates) describe placement; they are not edge weights.
This is why Dijkstra's algorithm is suitable: movement costs are nonnegative.

The start hub initially holds every drone and the end hub holds delivered
drones without capacity limits. Other hubs and connections have capacity limits.
Moves in one turn are simultaneous, so an outgoing drone frees hub space in
that turn. A restricted move occupies its connection in the first turn and
**must** arrive at the destination in the next turn. Waiting drones produce no
movement token.

For the one-route search, `previous[hub]` records the hub from which the best
known path arrived. Following those links from the end walks backward, so the
route is reversed once before returning it. `[]` currently means unreachable.
Priority zones currently cost 1 like normal zones; preference among equal-cost
routes is not implemented yet.

## Map guide

Use `examples/one_drone_linear.txt` for the current CLI walkthrough. The ten
supplied maps remain in `maps/`. Use `maps/easy/01_linear_path.txt` to check
multiple drones later, then the fork and capacity maps for competing drones.
Medium maps add dead ends, loops,
restricted zones, and priority choices. Hard maps combine these constraints.
The challenger map is optional.

| Map | Drone count | Subject target |
| --- | ---: | ---: |
| Easy: linear / fork / capacity | 2 / 4 / 4 | ≤6 / ≤8 / ≤6 turns |
| Medium: dead end / loop / priority | 5 / 6 / 5 | ≤12 / ≤15 / ≤12 turns |
| Hard: maze / capacity / ultimate | 8 / 12 / 15 | ≤30 / ≤35 / ≤45 turns |
| Challenger: impossible dream | 25 | 45-turn reference; optional |

These are optimization targets. Correct movement and capacity handling comes
first. Evaluation may use maps not included in this repository.
