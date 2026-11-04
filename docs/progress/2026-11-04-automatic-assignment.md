# Automatic assignment — 2026-11-04

## Goal and decision

Use discovered candidates in the CLI while keeping route choice easy to
explain. `FleetPlanner` tries two assignments: every drone on the best route,
and a round-robin spread over the candidates. It runs the simulator for each
plan before printing output, then chooses the valid plan with fewer turns.
A tie keeps the shared plan. If the spread cannot be scheduled, it falls back
to the shared plan.

This compares complete fleet schedules, so route length and bottlenecks
affect the choice through their actual turn counts. It does not search every
possible assignment.

## Evidence

The CLI now routes the four simple-fork drones across both branches in four
turns; the previous shared-route schedule took six. The linear map still
prints its original four-turn schedule because it has one candidate. All 35
tests and lint pass. A smoke run completed all ten supplied maps with the
new policy; the challenger map took 55 turns, above its optional 45-turn
reference.

## Next

Build an independent replay check for output validity across the supplied
maps, then refine route assignment and candidate generation where measured
turn counts show avoidable waiting. Priority preference and color remain
separate milestones.
