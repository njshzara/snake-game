# ai.py
import collections
from settings import *

class AutoPilot:
    """AI Logic for controlling the snake."""

    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cached_path = None # Optional: Cache path to food if still valid

    def _is_valid(self, point):
        """Check if a point is within the grid boundaries."""
        x, y = point
        return 0 <= x < self.grid_width and 0 <= y < self.grid_height

    def _get_neighbors(self, point):
        """Get valid neighbor cells for a given point."""
        x, y = point
        neighbors = []
        # Order matters slightly for fallback - prefer cardinal directions
        for dx, dy in [UP, DOWN, LEFT, RIGHT]:
            neighbor = (x + dx, y + dy)
            # No need to check validity here, BFS/callers will do it
            neighbors.append(neighbor)
        return neighbors

    def _reconstruct_path(self, came_from, start, end):
        """Helper to reconstruct path from BFS 'came_from' dictionary."""
        path = []
        current = end
        if current not in came_from and current != start: # Target unreachable
             return None
        while current != start:
            path.append(current)
            # Check if current is actually in came_from before accessing
            if current not in came_from:
                # This can happen if start == end, or unexpected BFS state
                # For start == end, path should be empty, handled earlier.
                # If it happens otherwise, indicates an issue.
                print(f"AI Path Reconstruction Error: {current} not in came_from map.")
                return None # Indicate error or inability to reconstruct
            current = came_from[current]
        path.reverse() # Path is from end to start, reverse it
        return path


    def find_path_bfs(self, start, end, obstacles):
        """
        Find the shortest path from start to end using Breadth-First Search.
        Avoids cells listed in 'obstacles'.
        Returns the path as a list of points (excluding start), or None if no path exists.
        """
        if not self._is_valid(start) or not self._is_valid(end):
             # print(f"BFS Invalid start {start} or end {end}")
             return None
        if start == end:
             # print("BFS Start == End")
             return [] # No path needed, already there

        queue = collections.deque([start])
        visited = set(obstacles) # Treat obstacles as already visited
        visited.add(start)
        came_from = {} # Dictionary to store path: {node: previous_node}

        while queue:
            current = queue.popleft()

            if current == end:
                # print(f"BFS Path found from {start} to {end}")
                return self._reconstruct_path(came_from, start, end)

            # Explore neighbors
            # Order matters slightly if multiple shortest paths exist, but BFS guarantees shortest
            for neighbor in self._get_neighbors(current):
                if self._is_valid(neighbor) and neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current # Record where we came from
                    queue.append(neighbor)

        # print(f"BFS No path found from {start} to {end}")
        return None # No path found


    def _can_reach_tail(self, start_node, snake_body_list, grid_width, grid_height):
        """
        Checks if the snake's tail is reachable from start_node using BFS.
        This is the core of the safety check.
        Assumes snake_body_list is the *future* state of the snake.
        """
        if len(snake_body_list) <= 1:
             return True # Snake is too short to trap itself

        future_head = start_node # This is the proposed next head position
        future_tail = snake_body_list[0]

        # Obstacles for this check are the future body *except* the tail
        # and the walls.
        obstacles = set(snake_body_list[1:]) # All segments except the actual tail end
        
        # Add walls
        for x in range(grid_width):
             obstacles.add((x, -1)); obstacles.add((x, grid_height))
        for y in range(grid_height):
             obstacles.add((-1, y)); obstacles.add((grid_width, y))


        # Perform BFS from the future head to the future tail
        queue = collections.deque([future_head])
        visited = set(obstacles)
        visited.add(future_head) # Start node is visited

        while queue:
            current = queue.popleft()
            if current == future_tail:
                # print(f"Safety Check: Tail {future_tail} REACHABLE from {future_head}")
                return True # Tail found!

            for neighbor in self._get_neighbors(current):
                # Check bounds AND if it's not an obstacle OR if it IS the tail
                # (Need to allow reaching the tail square itself)
                if self._is_valid(neighbor) and neighbor not in visited:
                     visited.add(neighbor)
                     queue.append(neighbor)

        # print(f"Safety Check: Tail {future_tail} UNREACHABLE from {future_head}")
        return False # BFS finished without finding tail

    def get_next_move(self, snake, food):
        """
        Calculates the next direction for the snake to move.
        Prioritizes:
        1. Safe path to food.
        2. Path to own tail (survival mode).
        3. Any valid move if trapped.
        Returns a direction tuple (e.g., UP, DOWN, LEFT, RIGHT) or None if no move possible.
        """
        head = snake.get_head_position()
        current_body = snake.get_body() # List of positions, head is last element
        food_pos = food.position

        # --- Define Obstacles for General Movement ---
        # Obstacles are walls and the snake's body *excluding the head itself*.
        # The tail square *can* be moved into in the next step if the snake isn't growing.
        obstacles = set(current_body[1:]) # Body excluding head
        if not snake.growing and len(current_body) > 1:
             tail = current_body[0]
             if tail in obstacles:
                 obstacles.remove(tail) # Allow moving into the square the tail *will* vacate

        # Add virtual walls as obstacles for pathfinding
        for x in range(-1, self.grid_width + 1):
            obstacles.add((x, -1)); obstacles.add((x, self.grid_height))
        for y in range(-1, self.grid_height + 1):
             obstacles.add((-1, y)); obstacles.add((self.grid_width, y))


        # --- Strategy 1: Find shortest path to food ---
        # print(f"\nAI Turn --- Head: {head}, Food: {food_pos}, Body Len: {len(current_body)}")
        # print(f"Obstacles for food path: {obstacles}")
        path_to_food = self.find_path_bfs(head, food_pos, obstacles)

        safe_food_move_found = False
        if path_to_food is not None: # Note: BFS returns [] if start==end, so check not None
             if len(path_to_food) > 0:
                 next_head_pos = path_to_food[0]
                 # print(f"AI: Path to food found: {path_to_food}")

                 # --- Safety Check ---
                 # Simulate the snake's body *after* making this move
                 potential_body = list(current_body) # Make a copy
                 potential_body.append(next_head_pos)
                 if not snake.growing:
                      potential_body.pop(0) # Tail disappears if not growing

                 # Check if the *future* tail is reachable from the *proposed* head
                 if self._can_reach_tail(next_head_pos, potential_body, self.grid_width, self.grid_height):
                      # print(f"AI: Move to {next_head_pos} towards food is SAFE.")
                      move = (next_head_pos[0] - head[0], next_head_pos[1] - head[1])
                      safe_food_move_found = True
                      # Keep this move, but check survival strategy just in case
                 else:
                      # print(f"AI: Move to {next_head_pos} towards food is UNSAFE (tail unreachable).")
                      path_to_food = None # Discard this path as unsafe
             else: # Path is empty, meaning head is already at food pos (shouldn't happen before move)
                 # This case might indicate an edge condition or bug.
                 # If head == food, game logic should handle eating before AI runs again.
                 # For safety, treat as no path found.
                 # print("AI WARNING: Path to food is empty, head may already be at food?")
                 path_to_food = None


        # --- Strategy 1b: If safe food path found, use it ---
        if safe_food_move_found:
             next_head_pos = path_to_food[0]
             move = (next_head_pos[0] - head[0], next_head_pos[1] - head[1])
             # print(f"AI: Action -> Move towards food: {move}")
             return move


        # --- Strategy 2: Path to food unsafe or not found - Follow tail (Survival) ---
        # print("AI: Path to food not found or unsafe. Seeking tail...")
        if len(current_body) > 0:
             tail_pos = current_body[0]

             # Obstacles for tail path: Body excluding head AND excluding the tail itself
             # (since we want to *reach* the tail square)
             tail_obstacles = set(current_body[1:-1]) # Exclude head and tail

             # Add walls
             for x in range(-1, self.grid_width + 1):
                 tail_obstacles.add((x, -1)); tail_obstacles.add((x, self.grid_height))
             for y in range(-1, self.grid_height + 1):
                  tail_obstacles.add((-1, y)); tail_obstacles.add((self.grid_width, y))

             # print(f"Obstacles for tail path: {tail_obstacles}")
             path_to_tail = self.find_path_bfs(head, tail_pos, tail_obstacles)

             if path_to_tail and len(path_to_tail) > 0:
                  next_head_pos = path_to_tail[0]
                  # We generally assume moving towards the tail is safe enough,
                  # but a strict AI could run _can_reach_tail check here too.
                  # Let's skip the extra check for performance/simplicity for now.
                  move = (next_head_pos[0] - head[0], next_head_pos[1] - head[1])
                  # print(f"AI: Action -> Move towards tail: {move}")
                  return move
             # else:
                  # print("AI: No path found to tail.")
        # else:
             # print("AI: Cannot seek tail, snake too short.")


        # --- Strategy 3: No path to food or tail - Make *any* valid move ---
        # print("AI: No optimal path found. Attempting any valid adjacent move...")
        current_direction = snake.direction
        # Define potential moves, maybe prioritize non-reversing ones
        potential_directions = [UP, DOWN, LEFT, RIGHT]
        # Filter out the reverse direction immediately
        reverse_direction = (-current_direction[0], -current_direction[1])
        valid_moves = []

        # Check neighbors in a preferred order (e.g., straight, left, right)
        preferred_order = [current_direction] # Try going straight first
        if current_direction in [UP, DOWN]:
            preferred_order.extend([LEFT, RIGHT])
        else: # LEFT or RIGHT
             preferred_order.extend([UP, DOWN])
        # Add the reverse direction last, only as absolute fallback (though usually blocked)
        # preferred_order.append(reverse_direction) # Usually blocked by body


        for move in preferred_order:
             next_head_pos = (head[0] + move[0], head[1] + move[1])
             # Check if the move is valid (within bounds) and not hitting the snake's body
             # Use the original 'obstacles' set which includes walls and body (minus maybe tail)
             if self._is_valid(next_head_pos) and next_head_pos not in obstacles:
                 # Check safety (tail reachability) for this fallback move too!
                 potential_body = list(current_body)
                 potential_body.append(next_head_pos)
                 if not snake.growing:
                     potential_body.pop(0)

                 if self._can_reach_tail(next_head_pos, potential_body, self.grid_width, self.grid_height):
                     # print(f"AI: Action -> Fallback SAFE move: {move}")
                     return move
                 # else:
                     # print(f"AI: Fallback move {move} to {next_head_pos} is unsafe.")


        # --- Strategy 4: Completely trapped ---
        # If we reach here, no safe move was found by any strategy.
        # The snake is likely boxed in. Let it make *any* move into an adjacent square
        # even if it's unsafe (can't reach tail), just to avoid immediate wall/body collision if possible.
        # If even that fails, it will collide.
        print("AI: WARNING - No SAFE fallback move found. Trying any valid non-colliding move.")
        for move in potential_directions:
             if move == reverse_direction and len(current_body) > 1: continue # Avoid instant 180 unless length 1
             next_head_pos = (head[0] + move[0], head[1] + move[1])
             if self._is_valid(next_head_pos) and next_head_pos not in obstacles:
                 print(f"AI: Action -> Fallback UNSAFE BUT VALID move: {move}")
                 return move # Take the first valid (but maybe unsafe) move

        # --- Strategy 5: Truly No Way Out ---
        print("AI: CRITICAL - Trapped! No valid moves possible.")
        # Return the current direction - this will likely cause a collision on the next step,
        # which is the expected outcome if truly trapped.
        return snake.direction