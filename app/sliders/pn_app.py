import numpy as np
import os
import json

from panel.layout.gridstack import GridSpec
from panel.layout.flex import FlexBox
from .config_importer import ConfigImporter
from .plotter import PlotterFactory

import logging
logging.basicConfig(level=logging.INFO)

def import_data(chart_id):
    """
    Main method of the class.
    Import the data from a generated JSON file.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    outfile_path = os.path.join(current_dir, "../../data/outfile.json")

    with open(outfile_path, 'r') as f:
        chart_data = json.load(f)
  
    return chart_data[chart_id]

def add_classes_to_plot(plot_obj, chart_id):
    for locale in ["ber", "de"]:
        plot_obj.plot[locale].css_classes.append('chart_' + chart_id + '_' + locale)

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


def get_base_chart():
    # TODO: Import real data and adjust plotter accordingly
    chart_data = import_data("base")
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    interactive_line_plotter = plotter_factory.create_plotter("line_interactive", interactive_line_data, config["basis_custom"])
    interactive_line_plotter.generate()

    add_classes_to_plot(interactive_line_plotter, "base")

    base_chart = FlexBox(*[interactive_line_plotter.plot["ber"], interactive_line_plotter.plot["de"], interactive_line_plotter.filters_multi_choice, interactive_line_plotter.filters_single_choice],
                          flex_direction='column', justify_content='space-between')

    return base_chart.servable()

def get_fue_chart():
    chart_data = import_data("fue-expenses")
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    pie_plotter = plotter_factory.create_plotter("pie_interactive", chart_data, config["donut_fue"])
    pie_plotter.generate()

    add_classes_to_plot(pie_plotter, "fue")

    fue_chart = FlexBox(*[pie_plotter.plot["ber"], pie_plotter.plot["de"],
                            pie_plotter.filters_single_choice, pie_plotter.filters_single_choice_highlight],
                          flex_direction='row', flex_wrap='wrap', justify_content='space-between')

    return fue_chart.servable()

def get_shares_chart():
    chart_data = import_data("shares")
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    pie_plotter = plotter_factory.create_plotter("pie_interactive", chart_data, config["donut_shares"])
    pie_plotter.generate()

    add_classes_to_plot(pie_plotter, "shares")

    shares_chart = FlexBox(*[pie_plotter.plot["ber"], pie_plotter.plot["de"],
                            pie_plotter.filters_single_choice, pie_plotter.filters_single_choice_highlight],
                          flex_direction='column', justify_content='space-between')


    return shares_chart.servable()

