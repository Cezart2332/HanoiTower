# Towers of Hanoi — Algorithm Visualizer

An interactive web application for visualizing and comparing pathfinding algorithms on the Towers of Hanoi problem, built with Python (Flask) and vanilla HTML/CSS/JS.

---

## Features

- **4 algorithms**: BFS, DFS, Greedy Best-First, A*
- **Step-by-step visualization** with play/pause and speed control
- **Performance analysis**: solution length, states explored, execution time (ms)
- **Flexible input**: slider, random generation, or `.txt` file upload
- **Move log**: full list of moves with highlight on the current step

---

## Project Structure

```
hanoi_app/
├── app.py                  # Flask backend — algorithms + API routes
├── requirements.txt
└── templates/
    └── index.html          # Frontend — visualization + controls
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Clone or download the project, then:
cd hanoi_app

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open your browser at **http://localhost:5000**

---

## Usage

### Input

| Method | How |
|--------|-----|
| Slider | Drag to set number of discs (1–8) |
| Random | Click 🎲 to generate a random disc arrangement |
| File upload | Upload a `.txt` file with space-separated integers (e.g. `3 2 1`) |

### Running an algorithm

1. Configure the discs using any input method
2. Select an algorithm (BFS, DFS, Greedy, A*)
3. Click **Rezolvă →**
4. Use the playback controls to step through the solution

### Playback controls

| Button | Action |
|--------|--------|
| ⏮ | Jump to initial state |
| ◀ | Previous step |
| ▶ | Play / Pause |
| ▶\| | Next step |
| ⏭ | Jump to final state |

Adjust the **speed slider** to control animation speed.

---

## Algorithms

### BFS — Breadth-First Search
Explores states level by level using a queue. **Guarantees the shortest solution** (minimum number of moves). Explores the most states of all four algorithms.

### DFS — Depth-First Search
Explores states depth-first using a stack. Does **not guarantee** the shortest path. Finds a solution quickly but it may be suboptimal.

### Greedy Best-First Search
Uses a priority queue ordered by a heuristic: `h(n) = discs not on peg C`. Always expands the state that looks closest to the goal. Fast but **not guaranteed to be optimal**.

### A* Search
Combines the number of moves taken so far `g(n)` with the heuristic `h(n)`:

```
f(n) = g(n) + h(n)
```

**Optimal and informed** — finds the shortest path while being guided toward the goal.

---

## Performance Comparison

| Algorithm | Optimal? | Memory | Speed |
|-----------|----------|--------|-------|
| BFS | ✅ Yes | High | Slow |
| DFS | ❌ No | Low | Fast |
| Greedy | ❌ No | Medium | Fast |
| A* | ✅ Yes | Medium | Medium |

> Note: performance degrades significantly beyond 7–8 discs due to the exponential growth of the state space (3^n possible states).

---

## File Format

To upload a custom disc configuration, create a `.txt` file with disc values separated by spaces. Each value must be unique.

```
3 2 1
```

```
5 3 1 4 2
```

The initial state places all discs on peg A. The goal is always to move all discs to peg C.

---

## State Representation

Each state is represented as a tuple of three tuples:

```python
state = (peg_A, peg_B, peg_C)
# e.g. ((3, 2, 1), (), ())  →  initial state
# e.g. ((), (), (3, 2, 1))  →  final state
```

Discs are stored bottom-to-top, so the last element is always the top disc.