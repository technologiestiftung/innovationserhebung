import numpy as np
from panel.layout.gridstack import GridSpec

from .plotter import PlotterFactory


# Create some random data - TODO: To be deleted later
pie_data = {
    "x": ["United States", "United Kingdom", "Japan", "China", "Germany"],
    "y": [157, 93, 89, 63, 44]
}

n = 20
x = np.random.rand(n)
y = np.random.rand(n)
size = np.random.randint(10, 100, n)
color = np.random.randint(0, 256, n)
bubble_data = {"x": x, "y": y, "size": size, "color": color}

line_data = {
    "x": [1, 2, 3, 4, 5],
    "y": [6, 7, 2, 4, 5]
}

interactive_line_data = {
    'x': [1, 2, 3, 4, 5],
    'line1': [5, 8, 6, 10, 7],
    'line2': [3, 5, 9, 6, 4],
    'line3': [8, 4, 2, 7, 9]
}

bar_data = {"x": ["A", "B", "C", "D"],
            "y": [15, 40, 25, 30]
}


def create_app():
    plotter_factory = PlotterFactory()

    pie_plotter = plotter_factory.create_plotter("pie", pie_data)
    pie_plotter.fit_data()
    pie_plotter.create_plot()

    pie_plotter_2 = plotter_factory.create_plotter("pie", pie_data)
    pie_plotter_2.fit_data()
    pie_plotter_2.create_plot()

    bubble_plotter = plotter_factory.create_plotter("bubble", bubble_data)
    bubble_plotter.fit_data()
    bubble_plotter.create_plot()

    interactive_line_plotter = plotter_factory.create_plotter("line_interactive", interactive_line_data)
    interactive_line_plotter.fit_data()
    interactive_line_plotter.create_plot()

    line_plotter = plotter_factory.create_plotter("line", line_data)
    line_plotter.fit_data()
    line_plotter.create_plot()

    bar_plotter = plotter_factory.create_plotter("bar", bar_data)
    bar_plotter.fit_data()
    bar_plotter.create_plot()

    gspec = GridSpec(width=800, height=1000)

    gspec[0:1, 0:1] = pie_plotter.plot
    gspec[0:1, 1:2] = pie_plotter_2.plot
    gspec[1:2, 0:2] = bubble_plotter.plot
    gspec[2:3, 0:2] = interactive_line_plotter.plot
    gspec[3:4, 0:2] = interactive_line_plotter.filters

    return gspec.servable()
