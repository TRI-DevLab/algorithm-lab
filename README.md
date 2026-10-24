# Algorithm Lab

An interactive path-finding visualizer and maze editor built in Python with Pygame.

___

## Features 

- ## Interactive Maze Editor: Click and drag on an editable grid to draw obstacles, clear walls, and reposition start or destination points. 
- ## Architecture:
    - `grid.py`: Python Grid data model and coordination validation
    - `algorithms.py`: graph search algorithms 
    - `main.py`: grid mapping, mouse and key events, and rendering algorithms

___

## Project Structure

```text
algorithm-lab/
├── grid.py          
├── algorithms.py    
├── main.py         
├── requirements.txt 
└── README.md

```
___

## How to Run

### Prerequisites
- Python 3.8+ installed

### Installation and Lunch
1. Clone Repository
```bash
git clone https://github.com/TRI-DevLab/algorithm-lab.git

```

2. Install Pygame
```bash
pip install pygame

```

3. Run Visualizer
```bash
python main.py

```

___

## Controls 

| Action | Input | Description |
| :--- | :--- | :--- |
| **Draw Wall** | `Left-Click` + Drag | Places obstacle walls on empty cells. |
| **Erase Wall** | `Right-Click` + Drag | Clears obstacle walls back to open cells. |
| **Move Start Node** | `S` + `Left-Click` | Repositions the Start node (Green). |
| **Move Goal Node** | `G` + `Left-Click` | Repositions the Goal node (Red). |
| **Run Path-finding** | `Space` | Starts the animated search traversal. |
| **Clear Board** | `C` | Clears all walls and resets visual path states. |