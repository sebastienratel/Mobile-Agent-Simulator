from mas.agent.AgentManager import AgentManager
from mas.graph.Graph import Graph
from mas.graph.Vertex import Vertex
from mas.graph.graph_generator import random_graph

from mas.agent.Agent import Agent


def _trivial_graph():
    G = Graph()
    u = Vertex(1)
    G.add_vertex(u)
    return G, u


def _edge_graph():
    G = Graph()
    u = Vertex(1)
    v = Vertex(2)
    G.add_vertex(u)
    G.add_vertex(v)
    G.add_edge(u, v)

    return G, u, v


def test_init_desired_id():
    G, _ = _trivial_graph()

    a1 = Agent(desired_id=3)
    a2 = Agent(desired_id=3)

    manager = AgentManager([a1, a2], G)

    assert manager.get_agent_id(a1) == 3
    assert not manager.get_agent_id(a2) == 3


def test_init_possible_latencies():
    G, _ = _trivial_graph()

    a1 = Agent(desired_latency=1)
    a2 = Agent(desired_latency=None)

    manager = AgentManager([a1, a2], G, possible_latencies=[2, 3])

    assert manager.get_agent_latency(a1) == 1
    assert manager.get_agent_latency(a2) in [2, 3]


def test_init_desired_position():
    G = random_graph(1000, 0)
    u = G.get_vertex_by_id(0)

    a = Agent(desired_position=u)

    manager = AgentManager([a], G)
    assert manager.get_agent_position(a) == u


def test_init_position_contains_mate():
    G, u, v = _edge_graph()

    a1 = Agent(desired_id=1, desired_position=u)
    a2 = Agent(desired_id=2, desired_position=u)
    a3 = Agent(desired_id=3, desired_position=v)

    manager = AgentManager([a1, a2, a3], G)

    assert manager.get_agent_position_contains_mate(a1)
    assert manager.get_agent_position_contains_mate(a2)
    assert not manager.get_agent_position_contains_mate(a3)


def test_move_agent():
    G, u, v = _edge_graph()

    a = Agent(desired_id=1, desired_position=u)

    manager = AgentManager([a], G)

    assert manager.get_agent_position(a) == u

    manager.move_agent(a, 0)
    assert manager.get_agent_position(a) == v


def test_notify_encounter_on_position():
    G, u, v = _edge_graph()

    a1 = Agent(desired_id=1, desired_position=u)
    a2 = Agent(desired_id=2, desired_position=v)

    manager = AgentManager([a1, a2], G)

    assert not manager.get_agent_position_contains_mate(a1)
    assert not manager.get_agent_position_contains_mate(a2)

    manager.move_agent(a1, 0)
    assert manager.get_agent_position_contains_mate(a1)
    assert manager.get_agent_position_contains_mate(a2)


def test_move_multiple_agents():
    G, u, v = _edge_graph()

    a1 = Agent(desired_position=u)
    a2 = Agent(desired_position=u)
    a3 = Agent(desired_position=v)

    manager = AgentManager([a1, a2, a3], G)

    manager.move_multiple_agents([(a1, 0), (a2, 0)])

    assert manager.get_agent_position(a1) == v
    assert manager.get_agent_position(a2) == v
    assert manager.get_agent_position(a3) == v


def test_notify_all_encounters():
    G, u, v = _edge_graph()
    w = Vertex(2)
    G.add_vertex(w)
    G.add_edge(u, w)
    G.add_edge(v, w)

    a1 = Agent(desired_position=u)
    a2 = Agent(desired_position=v)
    a3 = Agent(desired_position=w)
    a4 = Agent(desired_position=w)

    manager = AgentManager([a1, a2, a3, a4], G)

    assert not manager.get_agent_position_contains_mate(a1)
    assert not manager.get_agent_position_contains_mate(a2)

    manager.move_multiple_agents([(a3, 0), (a4, 1)])
    assert manager.get_agent_position_contains_mate(a1)
    assert manager.get_agent_position_contains_mate(a2)
