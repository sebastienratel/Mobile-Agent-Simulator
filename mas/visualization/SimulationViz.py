from mas.agent.Simulation import Simulation
import tkinter.font as tkFont


class SimulationViz():
    """Based on :class:`mas.agent.Simulation.Simulation`, encapsulates methods
    and parameters to draw Simulation objects."""

    def __init__(self, simulation, graphViz):
        """A simulation with drawing methods."""

        self._simulation = simulation
        self._graphViz = graphViz

        self._init_agents_graphics()

    def draw_agent(self, canvas, agent, vertex):
        """Draw a single agent.

        :param agent: The agent to draw.
        :type agent: :class:`mas.agent.Agent.Agent`

        :param canvas: Canvas in which to draw the agent.
        :type canvas: tkinter.Canvas
          (http://tkinter.fdex.eu/doc/caw.html)

        :param vertex: Position of the agent in the graph.
        :type vertex: :class:`mas.graph.Vertex.Vertex`
        """
        x, y = self._graphViz.get_vertex_position(vertex)

        r = self._agents_radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        canvas.create_oval(x0, y0, x1, y1,
                           fill=self._agents_color,
                           outline=self._agents_border_color,
                           width=self._agents_border_thickness,
                           tags=["agents", f"agent{agent.get_id()}"]
                           )
        if not self._simulation.anonymous():
            canvas.create_text(
                x,
                y,
                font=tkFont.Font(size=self._agents_id_size, weight='bold'),
                fill=self._agents_id_color,
                text=agent.get_id(),
                tags=[
                    "text",
                    "agents",
                    f"agent{agent.get_id()}",
                    f"text_agent{agent.get_id()}"
                ]
            )

    def draw_all_agents(self, canvas):
        """Draw all the agents.

        :param canvas: Canvas in which to draw the agents.
        :type canvas: tkinter.Canvas
          (http://tkinter.fdex.eu/doc/caw.html)
        """
        agents_manager = self._simulation.get_agents_manager()
        agents = self._simulation.get_all_agents()
        for agent in agents:
            position = agents_manager.get_agent_position(agent)
            self.draw_agent(canvas, agent, position)

    def draw_step_number(self, canvas):
        """Write the step number on south-east corner of the canvas.

        :param canvas: Canvas in which to write the step number.
        :type canvas: tkinter.Canvas
          (http://tkinter.fdex.eu/doc/caw.html)

        """
        canvas.update()
        canvas.create_text(
            canvas.winfo_width() - 40,
            canvas.winfo_height() - 20,
            font=tkFont.Font(size=15, weight='bold'),
            fill="black",
            text=self._simulation.get_step(),
            tags=["text", "step_text"]
        )

    def get_simulation(self):
        """Get the simulation on which is based this SimulationViz.

        :returns: The simulation on which is based this SimulationViz.
        :rtype: :class:`mas.agent.Simulation.Simulation`
        """
        return self._simulation

    def step_algo(self):
        """Execute :meth:`mas.agent.Simulation.Simulation.step_algo()` from the
        current simulation once.
        """
        self._simulation.step_algo()

    def _init_agents_graphics(self):
        self._agents_color = "green"
        self._agents_radius = 16
        self._agents_id_size = 12
        self._agents_id_color = "white"
        self._agents_border_color = "orange"
        self._agents_border_thickness = 1
