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


# TODO: Move ConfigImporter to another module
class ConfigImporter:
    def get_config(self):
        """
        Create a config dictionary based on default and custom values.

        :return: dict, resulting configuration file
        """
        # Load config files
        config_default = self.load_config_file("config_default.yaml")
        config_custom = self.load_config_file("config_custom.yaml")

        config_result = {}
        # Override default values with custom values for each plot
        for plot_name in config_custom:
            plot_config_custom = config_custom[plot_name]
            plot_type = plot_config_custom["plot_type"]
            plot_config_default = config_default[plot_type]

            self.override_values(plot_config_default, plot_config_custom)
            config_result[plot_name] = plot_config_default

        return config_result

    def load_config_file(self, filename):
        """
        Load a config file.

        :param filename: str, name of the YAML config file
        :return: dict, containing config settings
        """
        current_dir = os.path.dirname(__file__)
        config_path = os.path.join(current_dir, filename)

        with open(config_path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        return config

    def override_values(self, default_config, custom_config):
        """
        Override default values with custom values of a plot configuration.
        Implemented as a recursive function.

        :param default_config: dict, default configuration for a plot type
        :param custom_config: dict, custom configuration for a plot
        """
        for key, value in custom_config.items():
            if isinstance(value, dict) and key in default_config and isinstance(default_config[key], dict):
                self.override_values(default_config[key], value)
            else:
                default_config[key] = value


def create_app():
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    pie_plotter = plotter_factory.create_plotter("pie", pie_data, config["pie_custom"])
    pie_plotter.generate()

    pie_plotter_2 = plotter_factory.create_plotter("pie", pie_data, config["pie_custom"])
    pie_plotter_2.generate()

    bubble_plotter = plotter_factory.create_plotter("bubble", bubble_data, config["bubble_custom"])
    bubble_plotter.generate()

    interactive_line_plotter = plotter_factory.create_plotter("line_interactive", interactive_line_data, config["basis_custom"])
    interactive_line_plotter.generate()

    line_plotter = plotter_factory.create_plotter("line", line_data, config["line_custom"])
    line_plotter.generate()

    bar_plotter = plotter_factory.create_plotter("bar", bar_data, config["bar_custom"])
    bar_plotter.generate()

    gspec = GridSpec(width=800, height=1000)

    gspec[0:1, 0:1] = pie_plotter.plot
    gspec[0:1, 1:2] = pie_plotter_2.plot
    gspec[1:2, 0:2] = bubble_plotter.plot
    gspec[2:3, 0:1] = interactive_line_plotter.plot["ber"]
    gspec[2:3, 1:2] = interactive_line_plotter.plot["de"]
    gspec[3:4, 0:1] = interactive_line_plotter.filters_multi_choice
    gspec[3:4, 1:2] = interactive_line_plotter.filters_single_choice

    return gspec.servable()
