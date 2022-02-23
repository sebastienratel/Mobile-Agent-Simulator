from mas.visualization import GUI
from mas.graph.graph_generator import *
from mas.agent.Simulation import Simulation


if __name__ == "__main__":
    G = random_graph(10, 0.4)
    sim = Simulation(G)
    GUI.start(sim)
