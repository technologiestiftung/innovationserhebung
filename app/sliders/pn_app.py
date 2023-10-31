import json

import numpy as np
from panel.layout.gridstack import GridSpec
from panel.layout.flex import FlexBox

from .config_importer import ConfigImporter
from .plotter import PlotterFactory

# TODO: Refactoring
#   1/ ConfigImporter and PlotterFactory should be processed only once
#   2/ Think alternative to functions for individual plots, since it's not reused and it's not very idiomatic

with open("data/outfile.json", "r") as f:
    data = json.load(f)


# Create some random data - TODO: To be deleted later
pie_data = {
    "x": ["United States", "United Kingdom", "Japan", "China", "Germany"],
    "y": [157, 93, 89, 63, 44]
}

n = 20
x = np.random.rand(n)
y = np.random.rand(n)
size = np.random.randint(10, 100, n)
bubble_data = {"x": x, "y": y, "size": size}

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


def get_fue_chart():
    chart_data = data["fue_pie_interactive"]
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    pie_plotter = plotter_factory.create_plotter("pie_interactive", chart_data, config["fue_pie_interactive"])
    pie_plotter.generate()

    fue_chart = FlexBox(*[pie_plotter.plot["ber"], pie_plotter.plot["de"],
                          pie_plotter.filters_single_choice, pie_plotter.filters_single_choice_highlight],
                          flex_direction="row", flex_wrap="wrap", justify_content="space-between")

    return fue_chart.servable()


def get_shares_chart():
    chart_data = data["shares_pie_interactive"]
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    pie_plotter = plotter_factory.create_plotter("pie_interactive", chart_data, config["shares_pie_interactive"])
    pie_plotter.generate()

    shares_chart = FlexBox(*[pie_plotter.plot["ber"], pie_plotter.plot["de"],
                             pie_plotter.filters_single_choice, pie_plotter.filters_single_choice_highlight],
                             flex_direction="row", flex_wrap="wrap", justify_content="space-between")

    return shares_chart.servable()


def get_base_chart():
    # TODO: Import real data and adjust plotter accordingly
    # chart_data = data["base"]
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    interactive_line_plotter = plotter_factory.create_plotter("line_interactive", interactive_line_data, config["base_line_interactive"])
    interactive_line_plotter.generate()

    line_plotter = plotter_factory.create_plotter("line", line_data, config["base_line_interactive"])
    line_plotter.generate()

    base_chart = GridSpec(sizing_mode="stretch_both", min_height=800)

    base_chart[0:3, 0:2] = interactive_line_plotter.plot["ber"]
    base_chart[3:6, 0:2] = interactive_line_plotter.plot["de"]
    base_chart[6:7, 0:1] = interactive_line_plotter.filters_multi_choice
    base_chart[6:7, 1:2] = interactive_line_plotter.filters_single_choice

    return base_chart.servable()


def get_base_chart_ger():
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    interactive_line_plotter = plotter_factory.create_plotter("line_interactive", interactive_line_data, config["base_line_interactive"])
    interactive_line_plotter.generate()

    line_plotter = plotter_factory.create_plotter("line", line_data, config["base_line_interactive"])
    line_plotter.generate()

    base_chart = GridSpec(sizing_mode="stretch_both", min_height=600)

    base_chart[0:6, 0:2] = interactive_line_plotter.plot["de"]
    base_chart[6:7, 0:1] = interactive_line_plotter.filters_multi_choice
    base_chart[6:7, 1:2] = interactive_line_plotter.filters_single_choice

    return base_chart.servable()


def get_base_chart_ber():
    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    interactive_line_plotter = plotter_factory.create_plotter("line_interactive", interactive_line_data, config["base_line_interactive"])
    interactive_line_plotter.generate()

    line_plotter = plotter_factory.create_plotter("line", line_data, config["base_line_interactive"])
    line_plotter.generate()

    base_chart = GridSpec(sizing_mode="stretch_both", min_height=600)

    base_chart[0:6, 0:2] = interactive_line_plotter.plot["ber"]
    base_chart[6:7, 0:1] = interactive_line_plotter.filters_multi_choice
    base_chart[6:7, 1:2] = interactive_line_plotter.filters_single_choice
    return base_chart.servable()


def get_funky_bubble_chart():
    chart_data = data["growth_bubble"]["ber"]["individual"]

    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    bubble_plotter = plotter_factory.create_plotter("bubble", chart_data, config["growth_bubble"])
    bubble_plotter.generate()

    funky_bubbleplot = GridSpec(sizing_mode="stretch_both", min_height=350)
    funky_bubbleplot[0:1, 0:2] = bubble_plotter.plot

    return funky_bubbleplot.servable()


def get_bar_chart():
    chart_data = data["coop_partner"]

    config_importer = ConfigImporter()
    config = config_importer.get_config()

    plotter_factory = PlotterFactory()

    bar_plotter = plotter_factory.create_plotter("bar_interactive", chart_data, config["coop_partner"])
    bar_plotter.generate()

    barplot = GridSpec(sizing_mode="stretch_both", min_height=900)
    barplot[0:1, 0:2] = bar_plotter.plot["ber"]
    barplot[1:2, 0:1] = bar_plotter.filters_single_choice
    barplot[1:2, 1:2] = bar_plotter.filters_single_choice_2

    return barplot.servable()
