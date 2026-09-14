# TODO

This file records gaps between the current project and the subject. It describes the
missing behavior without prescribing an implementation.

## Parser framework

- [ ] Some whole-map parsing errors do not identify a source line. For example, a
      non-positive drone count reports the cause but not the line containing the value.
- [ ] There are no automated parser tests for malformed input and edge cases. Tests are
      recommended by the subject, although they are not submitted or graded.
- [ ] The parser preserves unknown metadata keys in `extra`. The subject defines the
      supported keys but does not clearly state whether unknown keys should be rejected.

## General project requirements

- [ ] Not every function and class has a PEP 257 docstring, as required by the general
    rules.
<!-- ? what is a pep 257 docstring -->
- [ ] The Makefile has no mandatory `lint` rule for running the specified flake8 and mypy
      checks.
- [ ] There is no root `README.md` containing the required introduction, instructions,
      resources, AI-use disclosure, design discussion, visual documentation, and example.
- [ ] The repository files are currently untracked, so they would not be included in a
      Git-based submission in their present state.

## Mandatory simulation

- [ ] The current `run` target only parses and prints a map; it does not run a drone
      simulation.
- [ ] There is no pathfinding or drone distribution behavior, including route selection,
      waiting, deadlock avoidance, or turn minimization.
- [ ] Zone occupancy and connection capacity limits are parsed but not enforced during
      simulated turns.
- [ ] Zone types are parsed but their movement behavior is absent: blocked zones remain
      usable data, restricted movement has no two-turn transit, and priority zones receive no
      path preference.
- [ ] Simultaneous movement has no turn-state validation, including capacity released by
      outgoing drones and conflicts between incoming drones.
- [ ] Drones do not have runtime identities, locations, in-transit state, or delivered
      state.
- [ ] The required per-turn `D<ID>-<zone>` / `D<ID>-<connection>` output is not produced,
      and there is no completion condition when every drone reaches the end hub.
- [ ] There is no colored terminal or graphical representation of movements and zone
      state.
- [ ] Performance against the easy, medium, and hard turn-count benchmarks has not been
      measured because no simulation algorithm exists yet.

## Optional work

- [ ] The optional secondary metrics and challenger-map performance goals are not
      implemented.
