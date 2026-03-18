from flask import Flask, render_template, request, jsonify
import heapq
import time
import random
import json

app = Flask(__name__)

class Queue:
    def __init__(self): self.queue = []
    def enqueue(self, e): self.queue.append(e)
    def dequeue(self): return self.queue.pop(0) if not self.is_empty() else None
    def is_empty(self): return len(self.queue) == 0

class Stack:
    def __init__(self): self.stack = []
    def push(self, e): self.stack.append(e)
    def pop(self): return self.stack.pop() if not self.is_empty() else None
    def is_empty(self): return len(self.stack) == 0


def get_moves(state, n):
    """Generate all valid moves from a state, returning (new_state, from_peg, to_peg, disc)"""
    current_a, current_b, current_c = state
    moves = []
    pegs = {'A': current_a, 'B': current_b, 'C': current_c}
    peg_names = ['A', 'B', 'C']
    
    for src_name in peg_names:
        src = pegs[src_name]
        if len(src) == 0:
            continue
        disc = src[-1]
        for dst_name in peg_names:
            if src_name == dst_name:
                continue
            dst = pegs[dst_name]
            if len(dst) == 0 or dst[-1] > disc:
                new_pegs = {
                    'A': list(current_a),
                    'B': list(current_b),
                    'C': list(current_c)
                }
                new_pegs[src_name] = new_pegs[src_name][:-1]
                new_pegs[dst_name] = new_pegs[dst_name] + [disc]
                new_state = (tuple(new_pegs['A']), tuple(new_pegs['B']), tuple(new_pegs['C']))
                moves.append((new_state, src_name, dst_name, disc))
    return moves


def run_bfs(discs):
    n = len(discs)
    initial = (tuple(discs), (), ())
    final = ((), (), tuple(sorted(discs, reverse=True)))
    
    visited = set()
    visited.add(initial)
    q = Queue()
    q.enqueue((initial, []))
    
    states_explored = 0
    start = time.time()
    
    while not q.is_empty():
        state, path = q.dequeue()
        states_explored += 1
        
        if state == final:
            elapsed = time.time() - start
            return {
                'moves': path,
                'states_explored': states_explored,
                'solution_length': len(path),
                'time': round(elapsed * 1000, 2)
            }
        
        for new_state, frm, to, disc in get_moves(state, n):
            if new_state not in visited:
                visited.add(new_state)
                q.enqueue((new_state, path + [{'from': frm, 'to': to, 'disc': disc, 'state': new_state}]))
    
    return None


def run_dfs(discs):
    n = len(discs)
    initial = (tuple(discs), (), ())
    final = ((), (), tuple(sorted(discs, reverse=True)))
    
    visited = set()
    visited.add(initial)
    s = Stack()
    s.push((initial, []))
    
    states_explored = 0
    start = time.time()
    
    while not s.is_empty():
        state, path = s.pop()
        states_explored += 1
        
        if state == final:
            elapsed = time.time() - start
            return {
                'moves': path,
                'states_explored': states_explored,
                'solution_length': len(path),
                'time': round(elapsed * 1000, 2)
            }
        
        for new_state, frm, to, disc in get_moves(state, n):
            if new_state not in visited:
                visited.add(new_state)
                s.push((new_state, path + [{'from': frm, 'to': to, 'disc': disc, 'state': new_state}]))
    
    return None


def heuristic(state, n):
    _, _, c = state
    return n - len(c)


def run_greedy(discs):
    n = len(discs)
    initial = (tuple(discs), (), ())
    final = ((), (), tuple(sorted(discs, reverse=True)))
    
    visited = set()
    visited.add(initial)
    pq = []
    heapq.heappush(pq, (heuristic(initial, n), 0, initial, []))
    counter = 0
    
    states_explored = 0
    start = time.time()
    
    while pq:
        score, _, state, path = heapq.heappop(pq)
        states_explored += 1
        
        if state == final:
            elapsed = time.time() - start
            return {
                'moves': path,
                'states_explored': states_explored,
                'solution_length': len(path),
                'time': round(elapsed * 1000, 2)
            }
        
        for new_state, frm, to, disc in get_moves(state, n):
            if new_state not in visited:
                visited.add(new_state)
                counter += 1
                h = heuristic(new_state, n)
                heapq.heappush(pq, (h, counter, new_state, path + [{'from': frm, 'to': to, 'disc': disc, 'state': new_state}]))
    
    return None


def run_astar(discs):
    n = len(discs)
    initial = (tuple(discs), (), ())
    final = ((), (), tuple(sorted(discs, reverse=True)))
    
    visited = set()
    visited.add(initial)
    pq = []
    g = 0
    h = heuristic(initial, n)
    heapq.heappush(pq, (g + h, g, 0, initial, []))
    counter = 0
    
    states_explored = 0
    start = time.time()
    
    while pq:
        f, g, _, state, path = heapq.heappop(pq)
        states_explored += 1
        
        if state == final:
            elapsed = time.time() - start
            return {
                'moves': path,
                'states_explored': states_explored,
                'solution_length': len(path),
                'time': round(elapsed * 1000, 2)
            }
        
        for new_state, frm, to, disc in get_moves(state, n):
            if new_state not in visited:
                visited.add(new_state)
                counter += 1
                new_g = g + 1
                new_h = heuristic(new_state, n)
                heapq.heappush(pq, (new_g + new_h, new_g, counter, new_state, path + [{'from': frm, 'to': to, 'disc': disc, 'state': new_state}]))
    
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    discs = data.get('discs', [])
    algorithm = data.get('algorithm', 'bfs')
    
    if not discs or len(discs) < 1 or len(discs) > 8:
        return jsonify({'error': 'Invalid disc count (1-8)'}), 400
    
    algorithms = {
        'bfs': run_bfs,
        'dfs': run_dfs,
        'greedy': run_greedy,
        'astar': run_astar
    }
    
    fn = algorithms.get(algorithm)
    if not fn:
        return jsonify({'error': 'Unknown algorithm'}), 400
    
    result = fn(discs)
    if result is None:
        return jsonify({'error': 'No solution found'}), 500
    
    # Convert state tuples to lists for JSON serialization
    for move in result['moves']:
        move['state'] = [list(move['state'][0]), list(move['state'][1]), list(move['state'][2])]
    
    return jsonify(result)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file'}), 400
    content = file.read().decode('utf-8').strip()
    try:
        discs = [int(x) for x in content.split()]
        if len(set(discs)) != len(discs):
            return jsonify({'error': 'Duplicate disc values'}), 400
        return jsonify({'discs': discs})
    except:
        return jsonify({'error': 'Invalid file format'}), 400


if __name__ == '__main__':
    app.run(debug=True)