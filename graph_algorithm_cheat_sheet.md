# Graph Algorithm Cheat Sheet

  -----------------------------------------------------------------------------
  Algorithm           Best used when     Avoid / Doesn't   Typical uses
                                         fit               
  ------------------- ------------------ ----------------- --------------------
  **BFS               All edges have     Edge costs        Shortest path in
  (Breadth-First      equal cost (or are differ. Graph is  unweighted graphs,
  Search)**           unweighted). Need  huge and memory   level-order
                      the shortest path  is tight.         traversal, finding
                      by **number of                       nearest node.
                      edges**.                             

  **DFS (Depth-First  You want to        You specifically  Cycle detection,
  Search)**           explore            need the shortest connected
                      everything, detect path. Very deep   components,
                      cycles, or process graphs without    topological sort,
                      dependencies.      safeguards.       backtracking.
                      Memory is limited.                   

  **Dijkstra's**      Edge weights are   Any negative edge Road networks,
                      **non-negative**   weights.          routing, cheapest
                      and you need the                     path.
                      minimum-cost path.                   

  **A\***             Same as Dijkstra's No useful         Maps, pathfinding in
                      **plus** you have  heuristic, or the games, navigation.
                      a good heuristic   heuristic         
                      estimating         overestimates the 
                      distance to the    remaining cost.   
                      goal.                                

  **Bellman--Ford**   Graph may contain  Graph is very     Currency arbitrage,
                      **negative edge    large and all     graphs with
                      weights**.         weights are       penalties/rewards.
                                         non-negative      
                                         (Dijkstra is      
                                         faster).          
  -----------------------------------------------------------------------------

## Quick decision guide

1.  **Do all edges cost the same?**
    -   ✅ Yes → **BFS**
    -   ❌ No → Continue
2.  **Can edge weights be negative?**
    -   ✅ Yes → **Bellman--Ford**
    -   ❌ No → Continue
3.  **Do you have a good heuristic (an estimate of distance to the
    goal)?**
    -   ✅ Yes → **A\***
    -   ❌ No → **Dijkstra's**
4.  **Are you not really looking for the shortest path at all?**
    -   Think **DFS** for exploration, cycle detection, recursion,
        backtracking, or topological sorting.

## Key concepts

### Edge weight

A cost associated with travelling along an edge, such as: - Distance -
Time - Money - Risk - Energy

### Heuristic

A **fast estimate** of how far you are from the goal.

Example: - Straight-line distance on a map. - Manhattan distance on a
grid.

A\* uses:

> cost so far + estimated remaining cost

to decide what to explore next.

### Frontier

The set of nodes you've **discovered but haven't explored yet**.

-   **BFS:** a FIFO queue.
-   **DFS:** a stack (often the call stack).
-   **Dijkstra/A\*:** a priority queue ordered by lowest estimated cost.

## Mental checklist

Before choosing an algorithm, ask:

-   Are edges weighted?
-   Can weights be negative?
-   Do I need the shortest path?
-   Do I have a good heuristic?
-   Am I exploring the whole graph or trying to reach one goal?
-   Will memory be a limiting factor?

In practice, **BFS, DFS, Dijkstra's, and A\*** cover the vast majority
of graph problems.
