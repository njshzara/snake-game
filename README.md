# Snake Game with AI Mode

A Python implementation of the classic Snake game featuring both manual and AI-controlled modes.

## Features
- Classic Snake gameplay
- AI autopilot mode (toggle with M key)
- Score tracking
- Adjustable game speed
- Pause functionality (P key)

## Installation
1. Clone the repository:
```bash
git clone https://github.com/njshzara/snake-game.git
cd snake-game
```

2. Set up virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install pygame
```

## Running the Game
```bash
python3 main.py
```

## Controls
- **Arrow keys/WASD**: Move snake (manual mode)
- **M**: Toggle between manual/auto mode
- **P**: Pause game
- **R**: Restart after game over
- **Q**: Quit game

## AI Mode
The game includes an AI autopilot that uses pathfinding algorithms to navigate the snake to the food.

## Requirements
- Python 3.x
- Pygame 2.6.1+
