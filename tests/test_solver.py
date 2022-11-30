import pytest
from utils import Individual, ExclusionGroup, uuid4_str, connections_list_to_dict, connections_list_from_dict
from solvers import NetworkXAssignmentSolver, RandomPathAssignmentSolver
from loguru import logger
import json


@pytest.fixture
def solvers():
    return [NetworkXAssignmentSolver(), RandomPathAssignmentSolver()]


class TestSolversBasic:
    def test_solvers_basic(self, solvers):
        num_groups = 3
        num_individuals = 10
        groups = [ExclusionGroup() for _ in range(num_groups)]
        individuals = [Individual(uuid4_str(), uuid4_str(), {groups[i % num_groups]}) for i in range(num_individuals)]
        for solver in solvers:
            solver.reset()
            solver.individuals = individuals
            soln = solver.solve()
            assert len(soln) == num_individuals
            assert len({s[0].name for s in soln}) == num_individuals
            assert len({s[1].name for s in soln}) == num_individuals

    def test_solvers_throw_when_impossible_1(self, solvers):
        num_groups = 1
        num_individuals = 10
        groups = [ExclusionGroup() for _ in range(num_groups)]
        individuals = [Individual(uuid4_str(), uuid4_str(), {groups[i % num_groups]}) for i in range(num_individuals)]
        for solver in solvers:
            with pytest.raises(RuntimeError):
                solver.reset()
                solver.individuals = individuals
                solver.solve()

    def test_solvers_throw_when_impossible_2(self, solvers):
        num_groups = 3
        num_individuals = 10
        groups = {ExclusionGroup() for _ in range(num_groups)}
        individuals = [Individual(uuid4_str(), uuid4_str(), groups) for i in range(num_individuals)]
        for solver in solvers:
            with pytest.raises(RuntimeError):
                solver.reset()
                solver.individuals = individuals
                solver.solve()

    def test_parse(self):
        num_groups = 3
        num_individuals = 10
        groups = [ExclusionGroup() for _ in range(num_groups)]
        individuals = [Individual(uuid4_str(), uuid4_str(), {groups[i % num_groups]}) for i in range(num_individuals)]
        solver = NetworkXAssignmentSolver(individuals)
        connections = solver.solve()
        data = connections_list_to_dict(connections)
        data_json = json.dumps(data, indent=2)
        logger.info(f"Got data:\n {data_json}")
        assert len(data["connections"]) == num_individuals
        assert len(data["individuals"]) == num_individuals
        assert len(data["groups"]) == num_groups
        connections_reparsed = connections_list_from_dict(data)
        assert len(connections_reparsed) == len(connections)
