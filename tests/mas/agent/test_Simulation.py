from mas.agent.Simulation import Simulation
from mas.agent.Agent import Agent

from mas.graph.Graph import Graph
from mas.graph.Vertex import Vertex


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


def test_get_agent():
    G, _ = _trivial_graph()

    sim = Simulation(G)

    assert type(sim.get_agent(0)) == Agent
    assert sim.get_agent(1) is None


def test_model():
    G, _ = _trivial_graph()

    sim = Simulation(G)

    assert sim.model() == {
        "anonymous": False,
        "synchronous": True,
        "anonymous_topology": False,
        "agents_number": 1,
        "possible_latencies": [1]
    }


def test_step_algo():
    G, _ = _trivial_graph()

    sim = Simulation(G)

    assert sim.get_step() == 1

    sim.step_algo()
    assert sim.get_step() == 2

    sim.step_algo()
    assert sim.get_step() == 3


def test_init_notifications():
    G, u, v = _edge_graph()

    a1 = Agent(desired_id=1, desired_position=u)
    a2 = Agent(desired_id=2, desired_position=u)
    a3 = Agent(desired_id=3, desired_position=v)

    sim = Simulation(G, agents_list=[a1, a2, a3])
    a1.join_to_simulation(sim)
    a2.join_to_simulation(sim)
    a3.join_to_simulation(sim)

    assert a1.position_contains_mate()
    assert a2.position_contains_mate()
    assert not a3.position_contains_mate()
