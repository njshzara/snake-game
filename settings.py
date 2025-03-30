# settings.py
import pygame

# Screen dimensions
GRID_SIZE = 20
GRID_WIDTH = 30  # Number of grid cells horizontally
GRID_HEIGHT = 20 # Number of grid cells vertically
SCREEN_WIDTH = GRID_SIZE * GRID_WIDTH
SCREEN_HEIGHT = GRID_SIZE * GRID_HEIGHT

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (40, 40, 40)
GREEN = (0, 150, 0)       # Darker green for body
LIGHT_GREEN = (0, 255, 0) # Brighter green for head
RED = (200, 0, 0)         # Food color
DARK_RED = (100, 0, 0)      # Game over text color
BLUE = (0, 0, 255)        # Path visualization (optional)
YELLOW = (255, 255, 0)    # UI Text color

# Game speed
INITIAL_FPS = 10
FPS_INCREMENT = 1 # How much FPS increases per food item (optional)

# Directions (using tuples for easy addition/subtraction)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Font settings
FONT_NAME = pygame.font.match_font('arial') # Or choose a specific .ttf file
FONT_SIZE_LARGE = 36
FONT_SIZE_SMALL = 24

# AI Settings
DEBUG_AI_PATH = False # Set to True to visualize the AI's calculated path