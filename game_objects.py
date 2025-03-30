# game_objects.py
import pygame
import random
from settings import *

class Snake:
    """Represents the snake."""
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.reset()

    def reset(self):
        """Resets the snake to its initial state."""
        self.length = 1
        # Start position in grid coordinates
        self.positions = [((self.grid_width // 2), (self.grid_height // 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color_head = LIGHT_GREEN
        self.color_body = GREEN
        self.growing = False # Flag to indicate if the snake should grow next move

    def get_head_position(self):
        """Returns the position of the snake's head."""
        return self.positions[-1]

    def get_body(self):
        """Returns the list of positions occupied by the snake's body."""
        return self.positions

    def turn(self, point):
        """Changes the snake's direction, prevents 180-degree turns."""
        # Prevent reversing direction
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        else:
            self.direction = point

    def move(self):
        """Moves the snake one step in the current direction."""
        cur_x, cur_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (((cur_x + dx) % self.grid_width), ((cur_y + dy) % self.grid_height))

        # Wall collision detection (alternative: wrap around)
        # For this version, we let the Game class handle wall collision based on boundary check
        # new_head = (cur_x + dx, cur_y + dy) # Use this line if you want wall collisions instead of wrap-around

        # Self collision check
        if len(self.positions) > 2 and new_head in self.positions[:-1]:
             # Let the Game class handle self-collision game over
             pass # Continue the move, collision check happens in Game.update

        self.positions.append(new_head)

        # Handle growing: if growing, don't remove the tail
        if self.growing:
            self.length += 1
            self.growing = False # Reset growth flag for next move
        else:
            # Remove the tail segment if not growing
            self.positions.pop(0)


    def grow(self):
        """Flags the snake to grow on its next move."""
        self.growing = True

    def draw(self, surface):
        """Draws the snake on the given surface."""
        # Draw body segments first
        for i, p in enumerate(self.positions[:-1]): # Draw all except the head
            r = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.color_body, r)
            # Optional: add a border for clarity
            pygame.draw.rect(surface, BLACK, r, 1)

        # Draw head segment last (on top)
        head_pos = self.get_head_position()
        head_rect = pygame.Rect((head_pos[0] * GRID_SIZE, head_pos[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color_head, head_rect)
        pygame.draw.rect(surface, BLACK, head_rect, 1) # Optional border


class Food:
    """Represents the food pellet."""
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.position = (0, 0) # Initial dummy position
        self.color = RED
        self.randomize_position([]) # Initial placement requires empty snake list

    def randomize_position(self, snake_positions):
        """Places the food randomly, avoiding the snake's body."""
        while True:
            self.position = (random.randint(0, self.grid_width - 1),
                             random.randint(0, self.grid_height - 1))
            # Ensure food does not spawn on the snake
            if self.position not in snake_positions:
                break

    def draw(self, surface):
        """Draws the food on the given surface."""
        r = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, r)
        # Optional: Inner smaller rect for effect
        inner_offset = GRID_SIZE // 4
        inner_r = pygame.Rect(
            (self.position[0] * GRID_SIZE + inner_offset, self.position[1] * GRID_SIZE + inner_offset),
            (GRID_SIZE - 2 * inner_offset, GRID_SIZE - 2 * inner_offset)
        )
        pygame.draw.rect(surface, LIGHT_GREEN, inner_r) # Use a contrasting color