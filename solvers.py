from typing import Optional, Set, List, Tuple
from utils import Individual, ExclusionGroup, uuid4_str
import networkx as nx
import random


class AssignmentSolver:
    def __init__(self, individuals: List[Individual] = None):
        self.individuals = individuals or []

    def solve(self) -> List[Tuple[Individual, Individual]]:
        connections = self._solve_impl()
        if len(connections) != len(self.individuals):
            raise RuntimeError(f"Generated {len(connections)} connections for {len(self.individuals)} individuals!")
        if len({s[0].name for s in connections}) != len(self.individuals) or \
                len({s[1].name for s in connections}) != len(self.individuals):
            raise RuntimeError(f"Not all individuals appear once in senders and recipients!")
        return connections

    def reset(self):
        self.individuals = []

    def _solve_impl(self) -> List[Tuple[Individual, Individual]]:
        raise NotImplementedError()


class NetworkXAssignmentSolver(AssignmentSolver):
    def _solve_impl(self):
        EPS = 1e-1
        G = nx.DiGraph()

        left = [(uuid4_str(), {'individual': idv}) for idv in self.individuals]
        right = [(uuid4_str(), {'individual': idv}) for idv in self.individuals]

        G.add_node('source', individual=None)
        G.add_node('sink', individual=None)
        G.add_nodes_from(left)
        G.add_nodes_from(right)

        edges = []

        for id1, n1 in left:
            for id2, n2 in right:
                idv1, idv2 = n1['individual'], n2['individual']
                # add edge from left to right, if the intersection of the groups is zero
                if idv1.is_valid_match_for(idv2):
                    edges.append((id1, id2, {'capacity': 1}))
        for nid, _ in left:
            edges.append(('source', nid, {'capacity': 1}))
        for nid, _ in right:
            edges.append((nid, 'sink', {'capacity': 1}))

        G.add_edges_from(edges)

        flow_value, flow_dict = nx.maximum_flow(G, 'source', 'sink')

        if abs(flow_value - len(self.individuals)) > EPS:
            raise RuntimeError("Unsolvable Flow Graph!")

        connections = []

        for id1, n1 in left:
            for id2, n2 in right:
                if flow_dict.get(id1, {}).get(id2, 0.0) > EPS:
                    connections.append((n1['individual'], n2['individual']))

        return connections


class RandomPathAssignmentSolver(AssignmentSolver):
    def _solve_impl(self):
        def gen_path(people):
            list_copy = people[:]
            path = []
            first = random.choice(list_copy)
            list_copy = list(filter(lambda p: p != first, list_copy))
            path.append(first)
            try:
                while len(list_copy) > 0:
                    choice = random.choice(
                        list(
                            filter(lambda p: p.is_valid_match_for(path[-1]), list_copy)
                        )
                    )
                    path.append(choice)
                    list_copy = list(filter(lambda p: p != path[-1], list_copy))
                if not path[-1].is_valid_match_for(first):
                    return None
                path.append(first)
                return path
            except IndexError:
                return None

        def find_path(people, max_iters=100):
            p = gen_path(people)
            iters = 0
            while not p:
                if iters > max_iters:
                    return None
                p = gen_path(people)
                iters += 1
            return p

        path = find_path(self.individuals)
        connections = []
        if path is not None:
            for i in range(len(path) - 1):
                connections.append((path[i], path[i + 1]))
        return connections
