import os
import yaml

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
    "ber": {
        "anzahl": {
            "x": [1, 2, 3, 4, 5],
            "nahrung": [5, 8, 6, 10, 7],
            "pharma": [3, 5, 9, 6, 4],
            "textil": [8, 4, 2, 7, 9]
        },
        "umsatz": {
            "x": [1, 2, 3, 4, 5],
            "nahrung": [6, 9, 7, 11, 8],
            "pharma": [4, 6, 10, 7, 5],
            "textil": [9, 5, 3, 8, 10]
        }
    },
    "de": {
        "anzahl": {
            "x": [1, 2, 3, 4, 5],
            "nahrung": [6, 9, 7, 11, 8],
            "pharma": [4, 6, 10, 7, 5],
            "textil": [9, 5, 3, 8, 10]
        },
        "umsatz": {
            "x": [1, 2, 3, 4, 5],
            "nahrung": [7, 10, 8, 12, 9],
            "pharma": [5, 7, 11, 8, 6],
            "textil": [10, 6, 4, 9, 11]
        }
    }
}

bar_data = {"x": ["A", "B", "C", "D"],
            "y": [15, 40, 25, 30]
}


# TODO: Move to another module
def import_config(config_filename):
    """
    Import default plot configurations from a YAML file.

    :param config_filename: str, name of the YAML config file
    :return: dict, default configurations
    """
    current_dir = os.path.dirname(__file__)
    config_path = os.path.join(current_dir, config_filename)

    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    return config


def create_app():
    # TODO: Get rid of hardcoded path
    config = import_config("config.yaml")

    plotter_factory = PlotterFactory()

    pie_plotter = plotter_factory.create_plotter("pie", pie_data, config)
    pie_plotter.generate()

    pie_plotter_2 = plotter_factory.create_plotter("pie", pie_data, config)
    pie_plotter_2.generate()

    bubble_plotter = plotter_factory.create_plotter("bubble", bubble_data, config)
    bubble_plotter.generate()

    interactive_line_plotter = plotter_factory.create_plotter("line_interactive", interactive_line_data, config)
    interactive_line_plotter.generate()

    line_plotter = plotter_factory.create_plotter("line", line_data, config)
    line_plotter.generate()

    bar_plotter = plotter_factory.create_plotter("bar", bar_data, config)
    bar_plotter.generate()

    gspec = GridSpec(width=800, height=1000)

    gspec[0:1, 0:1] = pie_plotter.plot
    gspec[0:1, 1:2] = pie_plotter_2.plot
    gspec[1:2, 0:2] = bubble_plotter.plot
    gspec[2:3, 0:2] = interactive_line_plotter.plot
    gspec[3:4, 0:1] = interactive_line_plotter.filters_multi_choice
    gspec[4:5, 0:1] = interactive_line_plotter.filters_single_choice_1
    gspec[4:5, 1:2] = interactive_line_plotter.filters_single_choice_2

    return gspec.servable()
