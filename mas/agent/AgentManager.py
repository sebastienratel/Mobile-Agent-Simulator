import random
from collections import defaultdict


class AgentManager:
    """
    Used for managing all the data about agents during a simulation.
    """

    def __init__(self, agents_list, topology, possible_latencies=[1]):
        """An agent manager. It encapsulates all the data about agents in an 
        agent list: their identifiers; their positions; the information they
        store; ...

        :param agents_list: List of agents to manage.
        :type agents_list: list.

        :param topology: Topology on which the simulation is run
        :type topology: :class:`mas.graph.Graph.Graph`

        :param possible_latencies: If agents_list is set to None, every agent
            is generated with a latency randomly picked in this list.
            Default to [1].
        :type possible_latencies: list of int, optional
        """

        self._agents_position = dict()
        self._pos_to_agents_list = defaultdict(list)
        self._init_position(agents_list, topology)

        self._agents_id = dict()
        self._init_ids(agents_list)

        self._agents_latency = dict()
        self._init_latencies(agents_list, possible_latencies)

        self._agents_position_contains_mate = dict()
        self._init_positions_contains_mate()

        self._agents_port_back = dict()
        self._agents_last_move = dict()

        for agent in agents_list:
            self._set_agent_port_back(agent, None)
            self._set_agent_last_move(agent, 0)

    def _init_ids(self, agents_list):
        ids = random.sample(range(0, 50000), len(agents_list))
        i = 0
        for agent in agents_list:
            id = agent.desired_id()
            if (id is None) or (id in self._agents_id.values()):
                id = ids[i]
            self._agents_id[agent] = id
            i += 1

    def _init_latencies(self, agents_list, possible_latencies):
        for agent in agents_list:
            latency = agent.desired_latency()
            if latency is None:
                latency = random.choice(possible_latencies)
            self._agents_latency[agent] = latency

    def _init_position(self, agents_list, topology):
        for agent in agents_list:
            pos = agent.desired_initial_position()
            if pos is None:
                pos = random.choice(list(topology.vertices()))
            self._agents_position[agent] = pos
            self._pos_to_agents_list[pos].append(agent)

    def _init_positions_contains_mate(self):
        for vertex in self._pos_to_agents_list:
            self._notify_encounter_on_position(vertex)

    def agent_moved(self, agent, step):
        """Specify that an agent moved at current step.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :param step: Execution step of a simulation.
        :type step: int
        """
        self._set_agent_last_move(agent, step)

    def get_agent_last_move(self, agent):
        """Get the last step the agent moved.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: A step.
        :rtype: int
        """
        return self._agents_last_move[agent]

    def get_agent_id(self, agent):
        """Get the unique identifier of the agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The unique identifier of the agent.
        :rtype: int
        """
        return self._agents_id[agent]

    def get_agent_latency(self, agent):
        """Get the latency of the agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The latency of the agent.
        :rtype: int
        """
        return self._agents_latency[agent]

    def get_agent_port_back(self, agent):
        """Get the port number of the edge the agent comes from.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The port for the agent to get back to the previous position.
            If the agent did not perform any move, returns None.
        :rtype: int
        """
        return self._agents_port_back[agent]

    def get_agent_position(self, agent):
        """Get the position of an agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The current position of the agent.
        :rtype: :class:`mas.graph.Vertex.Vertex`
        """
        return self._agents_position[agent]

    def get_agent_position_contains_mate(self, agent):
        """Get a boolean according to whether current position of the agent 
        contains one or several agents.

        :returns: True if the current position of the agent contains an other
            agent, False otherwise.
        :rtype: boolean
        """
        return self._agents_position_contains_mate[agent]

    def get_occupied_positions(self):
        """Get the list of every vertex of the topology containing at least one
        agent.

        :return: A list of vertices.
        :rtype: list
        """
        return list(self._pos_to_agents_list)

    def move_agent(self, agent, port):
        """Modify the position of an agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :param port: Port of the edge for the agent to traverse.
        :type port: int
        """
        self._set_agent_position_contains_mate(agent, False)

        oldpos = self.get_agent_position(agent)
        newpos = oldpos.get_neighbor_by_port(port)
        self._set_agent_position(agent, newpos)

        if agent in self._pos_to_agents_list[oldpos]:
            self._pos_to_agents_list[oldpos].remove(agent)
            if len(self._pos_to_agents_list[oldpos]) == 0:
                del(self._pos_to_agents_list[oldpos])
        self._pos_to_agents_list[newpos].append(agent)

        self._notify_encounter_on_position(newpos)

        port_back = newpos.get_port_by_neighbor(oldpos)
        self._set_agent_port_back(agent, port_back)

    def move_multiple_agents(self, agents_with_ports):
        """Move multiple agents along given edges.

          :param agents_with_ports: Vectors of the form (agent, port)
          :type agents_with_ports: list of tuples
            (class:`mas.agent.Agent.Agent`, int)
        """
        for (agent, port) in agents_with_ports:
            self.move_agent(agent, port)
        self._notify_all_encounters()

    def _notify_all_encounters(self):
        for vertex in self.get_occupied_positions():
            self._notify_encounter_on_position(vertex)

    def _notify_encounter_on_position(self, vertex):
        numerous_agents = len(self._pos_to_agents_list[vertex]) > 1
        for agent in self._pos_to_agents_list[vertex]:
            self._set_agent_position_contains_mate(agent, numerous_agents)

    def _set_agent_last_move(self, agent, step):
        self._agents_last_move[agent] = step

    def _set_agent_port_back(self, agent, port_back):
        self._agents_port_back[agent] = port_back

    def _set_agent_position(self, agent, position):
        self._agents_position[agent] = position

    def _set_agent_position_contains_mate(self, agent, position_contains_mate):
        self._agents_position_contains_mate[agent] = position_contains_mate
