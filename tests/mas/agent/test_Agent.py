from mas.agent.Agent import Agent
from mas.agent.Simulation import Simulation

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


def move(agent):
    p = agent.available_ports()[0]
    agent.move_along(p)


def test_status_and_become():
    a = Agent(2)

    assert a.status() == ""

    a.become("new status")
    assert a.status() == "new status"


def test_get_id_named():
    G, u = _trivial_graph()

    a = Agent(desired_id=2, desired_position=u)

    sim = Simulation(G, agents_list=[a], anonymous=False)
    a.join_to_simulation(sim)
    assert a.get_id() == 2


def test_get_id_anonymous():
    G, u = _trivial_graph()

    a = Agent(desired_id=1, desired_position=u)

    sim = Simulation(G, agents_list=[a], anonymous=True)
    a.join_to_simulation(sim)
    assert a.get_id() is None


def test_move_along():
    G, u, _ = _edge_graph()

    a = Agent(desired_id=1, desired_position=u)

    sim = Simulation(G, agents_list=[a])

    a.join_to_simulation(sim)

    assert a.move_along(0)


def test_multiple_move_along():
    G, u, _ = _edge_graph()

    a = Agent(desired_id=1, desired_position=u)

    sim = Simulation(G, agents_list=[a])

    a.join_to_simulation(sim)

    assert a.move_along(0)
    assert not a.move_along(0)


def test_move_along_with_latency():
    G, u, _ = _edge_graph()

    a = Agent(desired_id=1, desired_position=u, desired_latency=2)

    sim = Simulation(G, agents_list=[a])
    a.join_to_simulation(sim)

    assert not a.move_along(0)


def test_move_along_nonexisting_port():
    G, u, _ = _edge_graph()

    a = Agent(desired_id=1, desired_position=u)

    sim = Simulation(G, agents_list=[a])
    a.join_to_simulation(sim)

    assert not a.move_along(2)


def test_get_position_id_named_graph():
    G, _, v = _edge_graph()

    a = Agent(desired_id=1, desired_position=v)

    sim = Simulation(G, agents_list=[a], anonymous_topology=False)
    a.join_to_simulation(sim)
    assert a.get_position_id() == 1


def test_get_position_id_anonymous_topology():
    G, _, v = _edge_graph()

    a = Agent(desired_id=1, desired_position=v)

    sim = Simulation(G, agents_list=[a], anonymous_topology=True)
    a.join_to_simulation(sim)
    assert a.get_position_id() is None


def test_port_back():
    G, u, v = _edge_graph()

    u.reset_port_associations({5: v})
    v.reset_port_associations({3: u})

    agent = Agent(desired_id=1, desired_position=u)

    sim = Simulation(G, agents_list=[agent], algorithm=move)
    agent.join_to_simulation(sim)

    assert agent.get_port_back() is None

    sim.step_algo()
    assert agent.get_port_back() == 3

    sim.step_algo()
    assert agent.get_port_back() == 5


def test_get_moves_nb():
    G, _, _ = _edge_graph()

    sim = Simulation(G, algorithm=move)
    agent = sim.get_agent(0)

    assert agent.get_moves_nb() == 0

    sim.step_algo()
    assert agent.get_moves_nb() == 1

    sim.step_algo()
    assert agent.get_moves_nb() == 2


def test_get_sim_step_synchronous():
    G, _ = _trivial_graph()

    sim = Simulation(G)
    agent = sim.get_agent(0)

    assert agent.get_sim_step() == 1

    sim.step_algo()
    assert agent.get_sim_step() == 2

    sim.step_algo()
    assert agent.get_sim_step() == 3


def test_get_sim_step_asynchronous():
    G, _ = _trivial_graph()

    sim = Simulation(G, synchronous=False)
    agent = sim.get_agent(0)

    assert agent.get_sim_step() is None

    sim.step_algo()
    assert agent.get_sim_step() is None
