import os
import yaml

import numpy as np
from panel.layout.gridstack import GridSpec
from panel.layout.flex import FlexBox

from .plotter import PlotterFactory
# import logging
# logging.basicConfig(level=logging.INFO)


# Create some random data - TODO: To be deleted later
pie_data = {
    "x": ["United States", "United Kingdom", "Japan", "China", "Germany"],
    "y": [157, 93, 89, 63, 44]
}

pie_data_2 = {
    "ber": {
      "2011": {
        "x": [
          "Wirtschaft",
          "Hochschulen",
          "Staat"
        ],
        "y": [
          1402.0,
          950.0,
          1257.0
        ]
      },
      "2020": {
        "x": [
          "Wirtschaft",
          "Hochschulen",
          "Staat"
        ],
        "y": [
          1402.0,
          950.0,
          1257.0
        ]
      }
    },
    "de": {
      "2011": {
        "x": [
          "Wirtschaft",
          "Hochschulen",
          "Staat"
        ],
        "y": [
          51077.0,
          13518.0,
          10974.0
        ]
      },
      "2020": {
        "x": [
          "Wirtschaft",
          "Hochschulen",
          "Staat"
        ],
        "y": [
          51077.0,
          13518.0,
          10974.0
        ]
      }
    }
  }
shares_data = {
    "ber": {
      "2012": {
        "x": [
          "Maschinen-/Fahrzeugbau",
          "Elektroindustrie/Instrumententechnik",
          "Pharma/Chemie/Kunststoff",
          "Software/Datenverarbeitung",
          "restliche Branchen"
        ],
        "y": [
          14.1,
          30.4,
          31.0,
          7.2,
          31.4
        ]
      },
      "2021": {
        "x": [
          "Maschinen-/Fahrzeugbau",
          "Elektroindustrie/Instrumententechnik",
          "Pharma/Chemie/Kunststoff",
          "Software/Datenverarbeitung",
          "restliche Branchen"
        ],
        "y": [
          18.4,
          20.8,
          25.0,
          12.3,
          42.0
        ]
      }
    },
    "de": {
      "2012": {
        "x": [
          "Maschinen-/Fahrzeugbau",
          "Elektroindustrie/Instrumententechnik",
          "Pharma/Chemie/Kunststoff",
          "Software/Datenverarbeitung",
          "restliche Branchen"
        ],
        "y": [
          49.9,
          16.0,
          15.2,
          5.2,
          13.8
        ]
      },
      "2021": {
        "x": [
          "Maschinen-/Fahrzeugbau",
          "Elektroindustrie/Instrumententechnik",
          "Pharma/Chemie/Kunststoff",
          "Software/Datenverarbeitung",
          "restliche Branchen"
        ],
        "y": [
          44.9,
          15.0,
          14.1,
          9.1,
          16.9
        ]
      }
    }
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

            overwritten_config = self.override_values(plot_config_default, plot_config_custom)
            config_result[plot_name] = overwritten_config

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

        overwritten_config = default_config.copy()
        for key, value in custom_config.items():
            if isinstance(value, dict) and key in overwritten_config and isinstance(default_config[key], dict):
                self.override_values(overwritten_config[key], value)
            else:
                overwritten_config[key] = value
        return overwritten_config


def get_fue_chart():
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    pie_plotter = plotter_factory.create_plotter("pie_interactive", pie_data_2, config["donut_fue"])
    pie_plotter.generate()

    fue_chart = FlexBox(*[pie_plotter.plot["ber"], pie_plotter.plot["de"],
                            pie_plotter.filters_single_choice, pie_plotter.filters_single_choice_highlight],
                          flex_direction='row', flex_wrap='wrap', justify_content='space-between')

    return fue_chart.servable()

def get_shares_chart():
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    pie_plotter = plotter_factory.create_plotter("pie_interactive", shares_data, config["donut_shares"])
    pie_plotter.generate()

    shares_chart = FlexBox(*[pie_plotter.plot["ber"], pie_plotter.plot["de"],
                            pie_plotter.filters_single_choice, pie_plotter.filters_single_choice_highlight],
                          flex_direction='row', flex_wrap='wrap', justify_content='space-between')

    return shares_chart.servable()


def get_base_chart():
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    interactive_line_plotter = plotter_factory.create_plotter("line_interactive", interactive_line_data, config["basis_custom"])
    interactive_line_plotter.generate()

    line_plotter = plotter_factory.create_plotter("line", line_data, config["line_custom"])
    line_plotter.generate()

    base_chart = GridSpec(sizing_mode='stretch_both', min_height=800)

    base_chart[0:3, 0:2] = interactive_line_plotter.plot["ber"]
    base_chart[3:6, 0:2] = interactive_line_plotter.plot["de"]
    base_chart[6:7, 0:1] = interactive_line_plotter.filters_multi_choice
    base_chart[6:7, 1:2] = interactive_line_plotter.filters_single_choice
    

    return base_chart.servable()

def get_base_chart_ger():
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    interactive_line_plotter = plotter_factory.create_plotter("line_interactive", interactive_line_data, config["basis_custom"])
    interactive_line_plotter.generate()

    line_plotter = plotter_factory.create_plotter("line", line_data, config["line_custom"])
    line_plotter.generate()

    base_chart = GridSpec(sizing_mode='stretch_both', min_height=600)

    base_chart[0:6, 0:2] = interactive_line_plotter.plot["de"]
    base_chart[6:7, 0:1] = interactive_line_plotter.filters_multi_choice
    base_chart[6:7, 1:2] = interactive_line_plotter.filters_single_choice
    

    return base_chart.servable()

def get_base_chart_ber():
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    interactive_line_plotter = plotter_factory.create_plotter("line_interactive", interactive_line_data, config["basis_custom"])
    interactive_line_plotter.generate()

    line_plotter = plotter_factory.create_plotter("line", line_data, config["line_custom"])
    line_plotter.generate()

    base_chart = GridSpec(sizing_mode='stretch_both', min_height=600)

    base_chart[0:6, 0:2] = interactive_line_plotter.plot["ber"]
    base_chart[6:7, 0:1] = interactive_line_plotter.filters_multi_choice
    base_chart[6:7, 1:2] = interactive_line_plotter.filters_single_choice
    return base_chart.servable()

def get_funky_bubble_chart():
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    bubble_plotter = plotter_factory.create_plotter("bubble", bubble_data, config["bubble_custom"])
    bubble_plotter.generate()

    funky_bubbleplot = GridSpec(sizing_mode='stretch_both', min_height=350)
    funky_bubbleplot[0:1, 0:2] = bubble_plotter.plot

    return funky_bubbleplot.servable()
