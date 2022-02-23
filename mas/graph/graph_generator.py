from .Graph import Graph
from .Vertex import Vertex

import random

"""Generation of classical topologies."""


def path(length):
    """Generate a path.

    :param length: Number of vertices in the path.
    :type lenght: int
    """
    G = Graph()

    G.add_vertex(Vertex(0))
    for i in range(1, length):
        u = Vertex(i)
        G.add_vertex(u)
        pred = G.get_vertex_by_id(i-1)
        G.add_edge(pred, u)

    return G


def cycle(length):
    """Generate a cycle. Ports are given such that following port 0 leads to a
    counterclockwise traversal of the cycle.

    :param length: Number of vertices in the cycle.
    :type length: int
    """
    G = path(length)
    u = G.get_vertex_by_id(0)
    v = G.get_vertex_by_id(length-1)
    G.add_edge(u, v)

    u1 = u.get_neighbor_by_port(0)
    u2 = u.get_neighbor_by_port(1)
    u.reset_port_associations({0: u2, 1: u1})

    return G


def tree(order):
    """Generate a random tree.

    :param order: Number of vertices in the tree.
    :type order: int
    """
    G = Graph()

    u = Vertex(0)
    vertices_tmp = [u]
    G.add_vertex(u)
    for i in range(1, order):
        u = Vertex(i)
        v = random.choice(vertices_tmp)
        vertices_tmp.append(u)
        G.add_vertex(u)
        G.add_edge(u, v)

    return G


def binary_tree(height):
    """Generate a complete binary tree.

    :param height: Height of the tree.
    :type height: int
    """
    G = Graph()

    for i in range(2**height-1):
        G.add_vertex(Vertex(i))

    for i in range(2**height-1):
        u = G.get_vertex_by_name(i)
        v = G.get_vertex_by_name(2*i+1)
        w = G.get_vertex_by_name(2*i+2)
        G.add_edge(u, v)
        G.add_edge(u, w)

    return G


def line(length):
    """Generate a path.

    :param length: number of vertices in the path.
    :type length: int
    """

    G = Graph()

    for i in range(0, length):
        G.add_vertex(Vertex(i))

    for i in range(1, length):
        u = G.get_vertex_by_id(i-1)
        v = G.get_vertex_by_id(i)
        G.add_edge(u, v)

    u = G.get_vertex_by_id(0)
    v = G.get_vertex_by_id(1)
    u.reset_port_associations({1: v})

    return G


def clique(size):
    """Generate a complete graph.

    :param size: Number of vertices.
    :type size: int
    """
    G = Graph()

    for i in range(size):
        u = Vertex(i)
        G.add_vertex(u)
        for j in range(i):
            v = G.get_vertex_by_id(j)
            G.add_edge(v, u)

    return G


def grid(width, height):
    """Generate a grid.

    :param width: Width of the grid.
    :type width: int

    :param height: Height of the grid.
    :type height: int
    """
    G = Graph()

    for i in range(width):
        for j in range(height):
            u = Vertex(f"({i},{j})")
            G.add_vertex(u)
            v = G.get_vertex_by_name(f"({i},{j-1})")
            w = G.get_vertex_by_name(f"({i-1},{j})")
            G.add_edge(u, v)
            G.add_edge(u, w)

    return G


def random_graph(order, link_probability=0.5):
    """Generate a random graph.

    :param order: Number of vertices.
    :type order: int

    :param link_probability: Probability of presence of each edge.
      Defaults to 0.5.
    :type link_probability: floating number between 0 and 1, optional.
    """
    G = Graph()

    for i in range(order):
        u = Vertex(i)
        G.add_vertex(u)
        for j in range(i):
            v = G.get_vertex_by_id(j)
            if (random.random() <= link_probability):
                G.add_edge(v, u)

    return G
