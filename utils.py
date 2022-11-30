from typing import Optional, Set, List, Tuple, Dict
import uuid
from dataclasses import dataclass, field


def uuid4_str():
    return str(uuid.uuid4())


@dataclass
class ExclusionGroup:
    name: str = field(default_factory=uuid4_str)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    @staticmethod
    def from_dict(d: Dict):
        return ExclusionGroup(
            d.get("name", uuid4_str()),
        )


@dataclass
class Individual:
    name: str
    contact: str
    groups: Set[ExclusionGroup] = field(default_factory=set)
    notes: Optional[str] = None

    def __eq__(self, other):
        return self.name == other.name and self.contact == other.contact

    def __hash__(self):
        return hash((self.name, self.contact))

    def is_valid_match_for(self, other):
        return self != other and len(self.groups.intersection(other.groups)) == 0

    @staticmethod
    def from_dict(d: Dict, groups_list: Optional[List[ExclusionGroup]] = None):
        groups = set(d.get("groups", {}))
        if groups_list is not None and len(groups) > 0:
            groups = {groups_list[g] for g in groups}
        return Individual(
            str(d["name"]),
            str(d["contact"]),
            groups,
            str(d.get("notes")) if "notes" in d else None,
        )


def connections_list_to_dict(connections: List[Tuple[Individual, Individual]]):
    result = {}
    groups = set()
    individuals = set()
    for idv1, idv2 in connections:
        individuals.add(idv1)
        individuals.add(idv2)
    individuals = list(individuals)
    for idv in individuals:
        groups.update(idv.groups)
    groups = list(groups)
    result["groups"] = [{"name": g.name} for g in groups]
    result["individuals"] = [
        {
            "name": idv.name,
            "contact": idv.contact,
            "groups": [
                groups.index(g) for g in idv.groups
            ],
            "notes": idv.notes,
        } for idv in individuals
    ]
    result["connections"] = sorted([
        {
            "sender": individuals.index(c[0]),
            "recipient": individuals.index(c[1]),
        } for c in connections
    ], key=lambda c: c["sender"])
    return result


def connections_list_from_dict(data: Dict):
    connections = []
    groups = []
    individuals = []

    for group in data["groups"]:
        groups.append(ExclusionGroup.from_dict(group))

    for individual in data["individuals"]:
        individuals.append(Individual.from_dict(individual, groups_list=groups))

    for connection in data["connections"]:
        connections.append((individuals[connection["sender"]], individuals[connection["recipient"]]))

    return connections
