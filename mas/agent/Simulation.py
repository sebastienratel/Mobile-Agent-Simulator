from .Agent import Agent
from .agent_algorithms import *
from .AgentManager import AgentManager
import random
from collections import defaultdict


class Simulation:
    """
    This is the main class of the distributed part of this simulator. It
    gathers the topology, the agents and the model. It makes the agents apply
    their algorithms and specifies which actions are legal for them.
    """

    def __init__(self,
                 topology,
                 algorithm=nothing,
                 agents_list=None,
                 agents_number=1,
                 possible_latencies=[1],
                 anonymous=False,
                 synchronous=True,
                 anonymous_topology=False,
                 verbose=False):
        """A Simulation specifying a model and a topology, executing the
        agents's algorithms, and sending requests to an AgentManager.

          :param topology: Topology on which the simulation is run
          :type topology: :class:`mas.graph.Graph.Graph`

          :param agents_list: List of agents to add to the simulation.
            Default to None.
          :type agents_list: list of :class:`mas.agent.Agent.Agent`,
            optional

          :param algorithm: an algorithm of the form ``algorithm(agent)``, where
            ``agent`` is of type :class:`mas.Agent.Agent`.
            Default to ``nothing`` (does nothing).
          :type algorithm: function

          :param agents_number: Number of agents to add to the simulation. Not
            taken into account if agents_list is not None.
            Default to 1.
          :type agents_number: int, optional

          :param anonymous: Anonymity of agents.
            Default to False.
          :type anonymous: boolean, optional

          :param anonymous_topology: Anonymity of the vertices.
            Default to False.
          :type anonymous_topology: boolean, optional

          :param synchronous: Synchronous model.
            Default to True.
          :type synchronous: boolean, optional

          :param possible_latencies: If agents_list is set to None, every agent
            is generated with a latency randomly picked in this list.
            Default to [1].
          :type possible_latencies: list of int, optional

          :param verbose: print warnings when agents call unvailable (in the
            model) methods or when the simulation prevents an agent from moving.
            Default to False.
          :type verbose: boolean, optional
        """
        self._topology = topology
        self._anonymous = anonymous
        self._anonymous_topology = anonymous_topology
        self._synchronous = synchronous
        self._algorithm = algorithm
        self._possible_latencies = possible_latencies

        self._verbose = verbose

        self._step = 1

        self._agents_list = []
        self._init_agents_list(agents_list, agents_number)

        self._agents_manager = AgentManager(
            self._agents_list, topology, possible_latencies)

        self._agents_to_move = []

    def _init_agents_list(self, agents_list, agents_number):
        if agents_list is None:
            for _ in range(agents_number):
                agent = Agent()
                self._agents_list.append(agent)
                agent.join_to_simulation(self)
        else:
            self._agents_list = agents_list

    def anonymous(self):
        """Get the anonymity status of the simulation.

        :returns: True if the simulation is anonymous, False otherwise.
        :rtype: boolean
        """
        return self._anonymous

    def anonymous_topology(self):
        """Get the graph anonymity status of the simulation.

        :returns: True if the topology of the simulation is anonymous, False
            otherwise.
        :rtype: boolean
        """
        return self._anonymous_topology

    def ask_for_available_ports(self, agent):
        """Get the list of all the available ports from agent's current 
            position.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: A list of ports.
        :rtype: list"""
        pos = self._agents_manager.get_agent_position(agent)
        return pos.get_ports()

    def ask_for_id(self, agent):
        """Returns the id of the agent, if the model allows it.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: If the model is anonymous, returns None. Otherwise, returns
            the unique identifier of the agent.
        :rtype: int
        """
        if self.anonymous():
            self._print_error("warning: agents are anonymous.")
            return None

        return self._agents_manager.get_agent_id(agent)

    def ask_for_moving(self, agent, port):
        """ Moves an agent, if possible. Namely, the agent ``position``
        attribute of the agent will be modified if:

        * it did not already move at this step;

        * its latency is not too high.

        If the simulation is asynchronous and the move is possible, then the
        agent instantly changes its position (according to the port).
        If the simulation is synchronous and the move is possible, then the
        agent is added to a list of moves to perform at the end of the step.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :param port: A port.
        :type port: int

        :returns: True if the move is legal, False otherwise.
        :rtype: boolean
        """
        is_moving_legal = self._is_moving_legal(agent, port)

        if is_moving_legal:
            self._agents_manager.agent_moved(agent, self._step)
            if not self.synchronous():
                self._agents_manager.move_agent(agent, port)
            else:
                self._add_to_agents_to_move(agent, port)

        return is_moving_legal

    def ask_for_port_back(self, agent):
        """Get the port number of the edge the agent comes from.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The port for the agent to get back to the previous position.
            If the agent did not perform any move, returns None.
        :rtype: int
        """
        return self._agents_manager.get_agent_port_back(agent)

    def ask_for_position_id(self, agent):
        """ Get the unique identifier of the given agent's position, if
        possible.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: If the simulation has an anonymous topology, then returns
            None.
            Otherwise, returns the unique identifier of the vertex the given
            agent is currently on.
        :rtype: int
        """

        if self.anonymous_topology():
            self._print_error("warning: graph is anonymous.")
            return None

        pos = self._agents_manager.get_agent_position(agent)
        return self._topology.get_vertex_id(pos)

    def ask_for_sim_step(self):
        """Get the current step number, if possible.

        :returns: The step number, if the simulation is synchronous.
            None, otherwise.
        :rtype: int
        """
        if not self.synchronous():
            self._print_error("warning: simulation is asynchronous.")
            return None

        return self.get_step()

    def get_agent(self, id):
        """Get an agent given an identifier.

        :param id: A unique agent identifier.
        :type id: int

        :returns: The agent identified by id if it exists, None otherwise.
        :rtype: class:`mas.agent.Agent.Agent`
        """
        if id < len(self._agents_list):
            return self._agents_list[id]
        return None

    def get_agents_manager(self):
        """Get the agent manager of this simulation.

        :returns: The agents manager of the simulation.
        :rtype: class:`mas.agent.AgentManager.AgentManager`
        """
        return self._agents_manager

    def get_all_agents(self):
        """Get a list of all the agents in the simulation.

        :returns: All the agents in the simulation.
        :rtype: list
        """
        return self._agents_list

    def get_step(self):
        """Get the current step number.

        :returns: The step number.
        :rtype: int
        """
        return self._step

    def model(self):
        """Get all the informations about the model of the simulation.

        :returns: A dictionnary of boolean keyed by model hypothesis.
        :rtype: dict
        """
        return {
            "anonymous": self._anonymous,
            "synchronous": self._synchronous,
            "anonymous_topology": self._anonymous_topology,
            "agents_number": len(self._agents_list),
            "possible_latencies": self._possible_latencies
        }

    def position_contains_mate(self, agent):
        """Returns a boolean based on the number of agents on the same position
        as the given agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: True if the current position of the agent contains several
          agents, False otherwise.
        :type: boolean
        """
        return self._agents_manager.get_agent_position_contains_mate(agent)

    def step_algo(self):
        """Run the algorithm of every agent once, according to the model of
        the simulation. Also increases the step number.
        """

        if self.synchronous():
            self._init_synchronous_step_algo()

        if not self.synchronous():
            random.shuffle(self._agents_list)

        for agent in self._agents_list:
            if not self.synchronous():
                if not (random.random() <= 0.7):
                    id = self._agents_manager.get_agent_id(agent)
                    self._print_error(f"asynchrony prevented agent "
                                      f"{id} to apply its "
                                      f"algorithm this round.")
                    continue

            self._algorithm(agent)

        if self.synchronous():
            self._agents_manager.move_multiple_agents(self._agents_to_move)

        self._step += 1

    def synchronous(self):
        """Get the synchronicity status of the simulation.

        :returns: True if the simulation is synchronous, False otherwise.
        :rtype: boolean
        """
        return self._synchronous

    def topology(self):
        """Get the topology of the simulation.

        :returns: The topology of the simulation.
        :rtype: class:`mas.graph.Graph.Graph`
        """
        return self._topology

    def _add_to_agents_to_move(self, agent, port):
        self._agents_to_move.append((agent, port))

    def _init_synchronous_step_algo(self):
        self._agents_to_move = []

    def _is_moving_legal(self, agent, port):
        legal = True

        agent_position = self._agents_manager.get_agent_position(agent)
        id = self._agents_manager.get_agent_id(agent)
        if agent_position.get_neighbor_by_port(port) is None:
            legal = False
            self._print_error(f"warning: agent {id} is "
                              f"trying to move through non existing port "
                              f"{port}.")

        elif self._agents_manager.get_agent_last_move(agent) == self._step:
            legal = False
            self._print_error(f"warning: agent {id} "
                              f"already moved this round.")

        elif self._synchronous:
            agent_latency = self._agents_manager.get_agent_latency(agent)
            legal = (self._step % agent_latency) == 0
            if not legal:
                self._print_error(f"warning: agent {id}'s "
                                  f"latency  does not allow him to move this "
                                  f"round.")

        return legal

    def _print_error(self, error_message):
        if self._verbose:
            print(error_message)
