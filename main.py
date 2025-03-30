# main.py
import pygame
import sys
from settings import *
from game_objects import Snake, Food
from ai import AutoPilot

class Game:
    """Manages the main game loop and game state."""

    def __init__(self):
        """Initialize Pygame, screen, clock, fonts, and game objects."""
        pygame.init()
        pygame.mixer.init() # For potential sound effects later
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Advanced Snake")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)

        self.grid_width = GRID_WIDTH
        self.grid_height = GRID_HEIGHT

        self.snake = Snake(self.grid_width, self.grid_height)
        self.food = Food(self.grid_width, self.grid_height)
        self.ai = AutoPilot(self.grid_width, self.grid_height) # Initialize AI

        self.score = 0
        self.current_fps = INITIAL_FPS
        self.game_over = False
        self.running = True
        self.paused = False
        self.auto_mode = False # Start in manual mode
        self.debug_path = None # To store AI path for visualization


    def _draw_text(self, text, font, color, x, y, center=True):
        """Helper function to draw text on the screen."""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

    def _draw_grid(self):
        """Draws the background grid."""
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (0, y), (SCREEN_WIDTH, y))

    def _display_ui(self):
        """Displays the score and current mode."""
        score_text = f"Score: {self.score}"
        mode_text = "Mode: AUTO" if self.auto_mode else "Mode: MANUAL"
        self._draw_text(score_text, self.font_small, YELLOW, 80, 15)
        self._draw_text(mode_text, self.font_small, YELLOW, SCREEN_WIDTH - 100, 15)

        if self.paused and not self.game_over:
             self._draw_text("PAUSED", self.font_large, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
             self._draw_text("Press P to Resume", self.font_small, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)


    def _show_game_over_screen(self):
        """Displays the game over message and instructions."""
        self.screen.fill(BLACK) # Optional: Dim background
        self._draw_text("GAME OVER", self.font_large, DARK_RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        self._draw_text(f"Final Score: {self.score}", self.font_small, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self._draw_text("Press R to Restart", self.font_small, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        self._draw_text("Press Q to Quit", self.font_small, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)
        pygame.display.flip()

        # Wait for player input
        waiting = True
        while waiting:
            self.clock.tick(15) # Low FPS while waiting
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False
                        waiting = False
                    if event.key == pygame.K_r:
                        self._reset_game()
                        waiting = False # Exit the waiting loop to restart game loop

    def _handle_input(self):
        """Processes player input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.game_over: # Only allow R or Q on game over screen
                     if event.key == pygame.K_r:
                         self._reset_game()
                     elif event.key == pygame.K_q:
                         self.running = False
                     continue # Skip other key checks if game is over

                # --- In-Game Controls ---
                if event.key == pygame.K_p: # Pause Toggle
                    self.paused = not self.paused
                if event.key == pygame.K_m: # Mode Toggle
                    self.auto_mode = not self.auto_mode
                    print(f"Switched to {'Auto' if self.auto_mode else 'Manual'} mode.")
                if event.key == pygame.K_q: # Quit anytime
                    self.running = False

                # Manual Mode Controls (only if not paused and not auto)
                if not self.auto_mode and not self.paused:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.snake.turn(UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.snake.turn(DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.snake.turn(LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.snake.turn(RIGHT)


    def _update(self):
        """Updates the game state."""
        if self.game_over or self.paused:
            return # Don't update if game over or paused

        if self.auto_mode:
            # Get AI's next move
            next_direction = self.ai.get_next_move(self.snake, self.food)
            if next_direction:
                 self.snake.turn(next_direction)
            else:
                 # AI couldn't find a move - likely trapped, let it collide
                 pass

            # --- Optional: Visualize AI path ---
            if DEBUG_AI_PATH:
                 obstacles_for_debug = set(self.snake.get_body()[:-1])
                 # Add walls
                 for x in range(-1, self.grid_width + 1):
                     obstacles_for_debug.add((x, -1)); obstacles_for_debug.add((x, self.grid_height))
                 for y in range(-1, self.grid_height + 1):
                      obstacles_for_debug.add((-1, y)); obstacles_for_debug.add((self.grid_width, y))
                 self.debug_path = self.ai.find_path_bfs(self.snake.get_head_position(), self.food.position, obstacles_for_debug)


        # Move the snake
        self.snake.move()
        head_pos = self.snake.get_head_position()

        # Check for food collision
        if head_pos == self.food.position:
            self.snake.grow()
            self.score += 1
            self.current_fps = min(30, INITIAL_FPS + (self.score // 2)) # Speed up slightly (optional)
            # Place new food, avoiding the *entire* current snake body
            self.food.randomize_position(self.snake.get_body())
            self.debug_path = None # Clear debug path when food eaten

        # Check for collisions (Game Over conditions)
        # 1. Wall collision
        hx, hy = head_pos
        if hx < 0 or hx >= self.grid_width or hy < 0 or hy >= self.grid_height:
            print("Collision: Wall")
            self.game_over = True

        # 2. Self collision
        # Check if head position is present anywhere else in the body list
        if head_pos in self.snake.positions[:-1]:
             print("Collision: Self")
             self.game_over = True


    def _draw(self):
        """Draws everything to the screen."""
        self.screen.fill(BLACK) # Background
        self._draw_grid()      # Draw grid lines
        self.snake.draw(self.screen)
        self.food.draw(self.screen)

        # Optional: Draw AI path for debugging
        if DEBUG_AI_PATH and self.auto_mode and self.debug_path:
            for point in self.debug_path:
                r = pygame.Rect((point[0] * GRID_SIZE, point[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(self.screen, BLUE, r, 3) # Draw path outline

        self._display_ui()     # Draw score and mode

        pygame.display.flip()  # Update the full display Surface to the screen


    def _reset_game(self):
        """Resets the game state for a new game."""
        self.snake.reset()
        self.food.randomize_position(self.snake.get_body())
        self.score = 0
        self.current_fps = INITIAL_FPS
        self.game_over = False
        self.paused = False
        # self.auto_mode = False # Optional: Reset to manual mode on restart? Or keep last mode? Let's keep last mode.
        self.debug_path = None
        print("Game Reset!")


    def run(self):
        """The main game loop."""
        while self.running:
            self._handle_input()

            if not self.game_over:
                self._update()
                self._draw()
            else:
                 # If game is over, handle input immediately checks for R/Q
                 # If R is pressed, _reset_game is called, game_over becomes False
                 # If Q is pressed, self.running becomes False
                 # If neither, show the game over screen until R or Q
                 self._show_game_over_screen() # Show screen and wait for R/Q

            # Control frame rate
            self.clock.tick(self.current_fps if not self.paused else 15) # Lower FPS when paused

        pygame.quit()
        sys.exit()

# --- Start the game ---
if __name__ == '__main__':
    game = Game()
    game.run()