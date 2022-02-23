import tkinter as tk
from mas.visualization.GraphViz import GraphViz
from mas.visualization.SimulationViz import SimulationViz


class GUI(tk.Frame):

    def __init__(self, root, simulation):
        tk.Frame.__init__(self, root)

        self.graphViz = GraphViz()
        self.graphViz.init_from_graph(simulation.topology(), copy=False)
        self.simulationViz = SimulationViz(simulation, self.graphViz)

        # Canvas
        self.canvas = tk.Canvas(self)

        # Buttons
        self.pause = True
        self.run_button = tk.Button(self, text="Run")
        self.pause_button = tk.Button(self, text="Pause")
        self.step_button = tk.Button(self, text="Step")
        self.redraw_button = tk.Button(self, text="Re-draw")
        self.exit_button = tk.Button(self, text="Exit")

        # Sliders
        self.max_running_speed = 1000
        self.running_speed = tk.IntVar()
        self.running_speed.set(200)
        self.speed_slider = tk.Scale(
            self, from_=1, to=self.max_running_speed-1)

        # Menu Buttons and control variables
        self.layout_option = tk.StringVar()
        self.layout_optionMenu = tk.OptionMenu(
            self,
            self.layout_option,
            *self.graphViz.get_all_layout_methods()
        )

        self.config_canvas()
        self.config_buttons()
        self.arrange()
        self.pack()

        self.graphViz.draw(self.canvas)
        self.simulationViz.draw_all_agents(self.canvas)
        self.simulationViz.draw_step_number(self.canvas)

    # Initialisations

    def config_canvas(self):
        x, y = self.graphViz.get_max_x_y_coordinate()
        r = self.graphViz.get_vertices_radius()
        p = self.graphViz.get_padding()
        width = x + 2*(r + p)
        height = y + 2*(r + p)
        self.canvas.config(bg="light gray", height=height, width=width)

        self.canvas.bind("<ButtonPress-1>", self.scan_coordinates)
        self.canvas.bind("<B1-Motion>", self.move)
        self.canvas.bind("<MouseWheel>", self.zoom)

    def config_buttons(self):
        self.run_button.config(width=10, command=self.start_run_algorithm)
        self.pause_button.config(
            width=10,
            command=self.pause_algorithm,
            state=tk.DISABLED)
        self.step_button.config(width=10, command=self.step_algorithm)
        self.redraw_button.config(width=10, command=self.redraw)
        self.exit_button.config(width=10, command=self.quit)

        self.layout_optionMenu.config(width=10)
        self.layout_option.set(self.graphViz.get_layout_method())

        self.speed_slider.config(
            orient=tk.HORIZONTAL,
            variable=self.running_speed,
            label="running speed",
            showvalue=0
        )

    def arrange(self):
        self.canvas.pack(side=tk.LEFT)
        self.run_button.pack(side=tk.TOP)
        self.pause_button.pack()
        self.step_button.pack()
        self.redraw_button.pack()
        self.exit_button.pack(side=tk.BOTTOM)
        self.layout_optionMenu.pack()
        self.speed_slider.pack()

    # Canvas Actions

    def scan_coordinates(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def zoom(self, event):
        if (event.delta > 0):
            self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
        elif (event.delta < 0):
            self.canvas.scale("all", event.x, event.y, 0.9, 0.9)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # Button Actions

    def redraw(self):
        self.canvas.delete('all')
        self.graphViz.set_layout_method(self.layout_option.get())
        self.graphViz.draw(self.canvas)
        self.simulationViz.draw_all_agents(self.canvas)

    def step_algorithm(self):
        self.simulationViz.step_algo()
        self.canvas.delete("agents")
        self.simulationViz.draw_all_agents(self.canvas)
        self.canvas.delete("step_text")
        self.simulationViz.draw_step_number(self.canvas)

    def start_run_algorithm(self):
        if self.pause:
            self.pause = False
            self.pause_button.config(state=tk.NORMAL)
            self.run_button.config(state=tk.DISABLED)
            self.run_algorithm()

    def run_algorithm(self):
        if not self.pause:
            self.simulationViz.step_algo()
            self.canvas.delete("agents")
            self.simulationViz.draw_all_agents(self.canvas)
            self.canvas.delete("step_text")
            self.simulationViz.draw_step_number(self.canvas)
            self.after(1000 - self.running_speed.get(), self.run_algorithm)

    def pause_algorithm(self):
        if not self.pause:
            self.pause = True
            self.pause_button.config(state=tk.DISABLED)
            self.run_button.config(state=tk.NORMAL)


def start(simulation):
    """
        Starts the Graphical User Interface (GUI).

        :param simulation: the simulation to execute and display. It contains,
            in particular, the :class:`mas.graph.Graph.Graph` to draw in the 
            main canvas of the GUI.
        :type simulation: :class:`mas.agent.Simulation.Simulation`
    """
    root = tk.Tk()
    app = GUI(root, simulation)
    root.title("Mobile Agents Simulator")
    app.mainloop()
