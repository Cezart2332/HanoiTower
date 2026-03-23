from flask import Flask, render_template, request, jsonify
import heapq
import time

app = Flask(__name__)

# ─────────────────────────────────────────
#  Structuri de date proprii
# ─────────────────────────────────────────

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


# ─────────────────────────────────────────
#  Clasa Nod
# ─────────────────────────────────────────

class Node:
    """
    Encapsuleaza informatiile unui nod din spatiul de cautare:
      - state  : starea curenta (tuple de 3 tuple-uri reprezentand tijele A, B, C)
      - parent : nodul parinte (None pentru radacina)
      - move   : mutarea care a generat aceasta stare (from_peg, to_peg, disc)
      - depth  : adancimea in arborele de cautare
      - cost   : costul acumulat pana la acest nod g(n)
      - h      : valoarea euristica h(n)
      - f      : costul estimat total f(n) = g(n) + h(n)
    """
    def __init__(self, state, parent=None, move=None, depth=0, cost=0, h=0):
        self.state  = state
        self.parent = parent
        self.move   = move
        self.depth  = depth
        self.cost   = cost
        self.h      = h
        self.f      = cost + h

    def get_path(self):
        """Reconstruieste drumul de la radacina la nodul curent."""
        path = []
        node = self
        while node.move is not None:
            path.append(node)
            node = node.parent
        return list(reversed(path))

    def serialize_move(self):
        frm, to, disc = self.move
        return {
            'from': frm, 'to': to, 'disc': disc,
            'state': [list(self.state[0]), list(self.state[1]), list(self.state[2])],
            'depth': self.depth, 'cost': self.cost, 'h': self.h, 'f': self.f
        }


# ─────────────────────────────────────────
#  Functii de stare
# ─────────────────────────────────────────

def init_state(discs):
    """Initializeaza starea problemei: toate discurile pe tija A."""
    return (tuple(discs), (), ())

def is_final(state, n):
    """Verifica daca starea curenta este starea finala (toate discurile pe C)."""
    all_discs = tuple(sorted(state[0] + state[1] + state[2], reverse=True))
    return state == ((), (), all_discs)

def is_valid(state):
    """Verifica validitatea starii: discuri unice, ordine corecta pe fiecare tija."""
    all_discs = state[0] + state[1] + state[2]
    if len(set(all_discs)) != len(all_discs):
        return False
    for peg in state:
        for i in range(len(peg) - 1):
            if peg[i] < peg[i + 1]:
                return False
    return True

def move_cost(disc):
    """Costul asociat mutarii unui disc. In varianta clasica, fiecare mutare costa 1."""
    return 1

def heuristic(state, n):
    """
    Euristica admisibila h(n) = numarul de discuri care NU se afla pe tija C.
    Nu supraestimeaza costul real => A* este optim.
    """
    return n - len(state[2])


# ─────────────────────────────────────────
#  Generarea succesorilor
# ─────────────────────────────────────────

def get_successors(node, n):
    """
    Genereaza toti succesorii unui nod prin aplicarea tuturor
    tranzitiilor valide (mutari legale de discuri intre tije).
    """
    a, b, c = node.state
    pegs = {'A': a, 'B': b, 'C': c}
    successors = []

    for src in ['A', 'B', 'C']:
        if not pegs[src]:
            continue
        disc = pegs[src][-1]
        for dst in ['A', 'B', 'C']:
            if src == dst:
                continue
            if not pegs[dst] or pegs[dst][-1] > disc:
                new_pegs = {k: list(v) for k, v in pegs.items()}
                new_pegs[src].pop()
                new_pegs[dst].append(disc)
                new_state = (tuple(new_pegs['A']), tuple(new_pegs['B']), tuple(new_pegs['C']))
                cost = node.cost + move_cost(disc)
                h = heuristic(new_state, n)
                successors.append(Node(
                    state=new_state, parent=node, move=(src, dst, disc),
                    depth=node.depth + 1, cost=cost, h=h
                ))
    return successors


# ─────────────────────────────────────────
#  Algoritmi
# ─────────────────────────────────────────

def run_bfs(discs, max_nodes=100000, max_time=30):
    n = len(discs)
    root = Node(init_state(discs), h=heuristic(init_state(discs), n))
    visited = {root.state}
    q = Queue()
    q.enqueue(root)
    states_explored = 0
    start = time.time()

    while not q.is_empty():
        if states_explored >= max_nodes:
            return {'error': f'Limita de {max_nodes} noduri depasita'}
        if time.time() - start > max_time:
            return {'error': f'Limita de timp ({max_time}s) depasita'}

        node = q.dequeue()
        states_explored += 1

        if is_final(node.state, n):
            return build_result(node, states_explored, start)

        for child in get_successors(node, n):
            if child.state not in visited:
                visited.add(child.state)
                q.enqueue(child)

    return {'error': 'Nicio solutie gasita'}


def run_dfs(discs, max_nodes=100000, max_time=30, max_depth=None):
    n = len(discs)
    root = Node(init_state(discs), h=heuristic(init_state(discs), n))
    visited = {root.state}
    s = Stack()
    s.push(root)
    states_explored = 0
    start = time.time()

    while not s.is_empty():
        if states_explored >= max_nodes:
            return {'error': f'Limita de {max_nodes} noduri depasita'}
        if time.time() - start > max_time:
            return {'error': f'Limita de timp ({max_time}s) depasita'}

        node = s.pop()
        states_explored += 1

        if is_final(node.state, n):
            return build_result(node, states_explored, start)

        if max_depth is not None and node.depth >= max_depth:
            continue

        for child in get_successors(node, n):
            if child.state not in visited:
                visited.add(child.state)
                s.push(child)

    return {'error': 'Nicio solutie gasita'}


def run_greedy(discs, max_nodes=100000, max_time=30):
    n = len(discs)
    initial = init_state(discs)
    root = Node(initial, h=heuristic(initial, n))
    visited = {root.state}
    pq = []
    counter = 0
    heapq.heappush(pq, (root.h, counter, root))
    states_explored = 0
    start = time.time()

    while pq:
        if states_explored >= max_nodes:
            return {'error': f'Limita de {max_nodes} noduri depasita'}
        if time.time() - start > max_time:
            return {'error': f'Limita de timp ({max_time}s) depasita'}

        _, _, node = heapq.heappop(pq)
        states_explored += 1

        if is_final(node.state, n):
            return build_result(node, states_explored, start)

        for child in get_successors(node, n):
            if child.state not in visited:
                visited.add(child.state)
                counter += 1
                heapq.heappush(pq, (child.h, counter, child))

    return {'error': 'Nicio solutie gasita'}


def run_astar(discs, max_nodes=100000, max_time=30):
    n = len(discs)
    initial = init_state(discs)
    root = Node(initial, h=heuristic(initial, n))
    visited = {root.state}
    pq = []
    counter = 0
    heapq.heappush(pq, (root.f, counter, root))
    states_explored = 0
    start = time.time()

    while pq:
        if states_explored >= max_nodes:
            return {'error': f'Limita de {max_nodes} depasita'}
        if time.time() - start > max_time:
            return {'error': f'Limita de timp ({max_time}s) depasita'}

        _, _, node = heapq.heappop(pq)
        states_explored += 1

        if is_final(node.state, n):
            return build_result(node, states_explored, start)

        for child in get_successors(node, n):
            if child.state not in visited:
                visited.add(child.state)
                counter += 1
                heapq.heappush(pq, (child.f, counter, child))

    return {'error': 'Nicio solutie gasita'}


# ─────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────

def build_result(node, states_explored, start):
    elapsed = time.time() - start
    path = node.get_path()
    moves = [n.serialize_move() for n in path]
    return {
        'moves': moves,
        'states_explored': states_explored,
        'solution_length': len(moves),
        'depth': node.depth,
        'total_cost': node.cost,
        'time': round(elapsed * 1000, 2)
    }


def parse_input_file(content):
    """
    Format fisier input:
      Linia 1: valorile discurilor separate prin spatii  (ex: 3 2 1)
      Linia 2 (optional): max_moves=N   -> limiteaza numarul de mutari permise
      Linia 2 (optional): max_nodes=N   -> limiteaza numarul de noduri explorate
    """
    lines = [l.strip() for l in content.strip().splitlines() if l.strip() and not l.strip().startswith('#')]
    discs = [int(x) for x in lines[0].split()]
    options = {}
    for line in lines[1:]:
        if '=' in line:
            k, v = line.split('=', 1)
            options[k.strip()] = int(v.strip())
    return discs, options


# ─────────────────────────────────────────
#  Flask routes
# ─────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    discs     = data.get('discs', [])
    algorithm = data.get('algorithm', 'bfs')
    max_nodes = data.get('max_nodes', 100000)
    max_time  = data.get('max_time', 30)

    if not discs or len(discs) < 1 or len(discs) > 8:
        return jsonify({'error': 'Numar invalid de discuri (1-8)'}), 400
    if len(set(discs)) != len(discs):
        return jsonify({'error': 'Discuri duplicate'}), 400

    algorithms = {
        'bfs':    lambda d: run_bfs(d, max_nodes, max_time),
        'dfs':    lambda d: run_dfs(d, max_nodes, max_time),
        'greedy': lambda d: run_greedy(d, max_nodes, max_time),
        'astar':  lambda d: run_astar(d, max_nodes, max_time),
    }

    fn = algorithms.get(algorithm)
    if not fn:
        return jsonify({'error': 'Algoritm necunoscut'}), 400

    result = fn(discs)
    return jsonify(result)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'Niciun fisier'}), 400
    try:
        content = file.read().decode('utf-8')
        discs, options = parse_input_file(content)
        if len(set(discs)) != len(discs):
            return jsonify({'error': 'Discuri duplicate in fisier'}), 400
        return jsonify({'discs': discs, 'options': options})
    except Exception as e:
        return jsonify({'error': f'Format fisier invalid: {e}'}), 400


if __name__ == '__main__':
    app.run(debug=True)