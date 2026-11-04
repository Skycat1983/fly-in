# Restricted transit checkpoint — 2026-11-04

## Goal and decision

A restricted destination costs two real simulation turns. Incrementing the
counter by 2 would skip the connection state and its output line, so each call
to `Drone.move_one_turn()` still represents exactly one turn.

The drone now records the destination `Hub` in `in_transit_to`. On departure
it moves from the source hub to the `Connection`, returns that connection's
name, and keeps its route index at the source. On the very next call it moves
to the stored destination hub, clears `in_transit_to`, advances the index, and
returns the hub name. The source hub is free while the drone is in flight.

## Evidence

Running `python3 main.py examples/one_drone_restricted.txt` prints:

```text
D1-start-restricted
D1-restricted
D1-goal
```

The drone test checks its intermediate connection location, unchanged route
index, pending destination, and forced arrival. The simulator test checks
the three output lines and three counted turns. All tests and lint pass.

## Next

Introduce multiple drones on one route. Once they can compete for a hub or
connection, reserve space for a restricted drone's required next-turn arrival
before allowing another drone to enter that destination.
