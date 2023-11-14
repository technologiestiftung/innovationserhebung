import json

from panel.layout.gridstack import GridSpec
from panel.layout.flex import FlexBox

from .config_importer import ConfigImporter
from .plotter import PlotterFactory

# TODO: Refactoring
#   2/ Think alternative to functions for individual plots, since it's not reused and it's not very idiomatic

# Create some random data - TODO: To be deleted later
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

# Load data
with open("data/outfile.json", "r") as f:
    data = json.load(f)

# Load config
config_importer = ConfigImporter()
config = config_importer.get_config()

# Initialize plotter factory
plotter_factory = PlotterFactory()

# Generate plots
plotters = {}
for plot_key in config:
    # TODO: Delete these conditions after refactoring the BubblePlotter
    #  and fixing the base plot bug
    if plot_key == "growth_bubble":
        plot_data = data["growth_bubble"]["ber"]["individual"]
    elif plot_key == "base_line_interactive":
        continue
    else:
        plot_data = data[plot_key]

    # TODO: Can refactor create_plotter() so I only need to pass the config as an argument
    plotter = plotter_factory.create_plotter(config[plot_key]["plot_type"], plot_data, config[plot_key])
    plotter.generate()

    plotters[plot_key] = plotter


def get_base_chart():
    # TODO: Import real data and adjust plotter accordingly
    interactive_line_plotter = plotter_factory.create_plotter("line_interactive",
                                                              data["base_line_interactive"],
                                                              config["base_line_interactive"])
    interactive_line_plotter.generate()

    line_plotter = plotter_factory.create_plotter("line", line_data, config["base_line_interactive"])
    line_plotter.generate()

    base_chart = GridSpec(sizing_mode="stretch_both", min_height=800)

    base_chart[0:3, 0:2] = interactive_line_plotter.plot["ber"]
    base_chart[3:6, 0:2] = interactive_line_plotter.plot["de"]
    base_chart[6:7, 0:1] = interactive_line_plotter.filters_multi_choice
    base_chart[6:7, 1:2] = interactive_line_plotter.filters_single_choice

    return base_chart


# TODO:
#  Think if I can simplify some of the code below, there is a lot of duplicate
#  Do we really need to use FlexBox AND GridSpec? Maybe we can just use one
chart_collection = {}

plot_key = "fue_pie_interactive"
plotter = plotters[plot_key]

flex_obj = FlexBox(plotter.plot["ber"],
               plotter.plot["de"],
               plotter.filters_single_choice,
               plotter.filters_single_choice_highlight,
               flex_direction="column",
               align_items="center",
               sizing_mode="stretch_width")
chart_collection[plot_key] = flex_obj

plot_key = "shares_pie_interactive"
plotter = plotters[plot_key]
flex_obj = FlexBox(plotter.plot["ber"],
               plotter.plot["de"],
               plotter.filters_single_choice,
               plotter.filters_single_choice_highlight,
               flex_direction="column",
               align_items="center",
               sizing_mode="stretch_width")
chart_collection[plot_key] = flex_obj

plot_key = "growth_bubble"
plotter = plotters[plot_key]
flex_obj = FlexBox(plotter.plot,
                flex_direction="column",
                align_items="center",
                sizing_mode="stretch_width")
chart_collection[plot_key] = flex_obj

plot_key = "coop_partner_bar_interactive"
plotter = plotters[plot_key]
flex_obj = FlexBox(plotter.plot["ber"],
               plotter.filters_single_choice,
               plotter.filters_single_choice_2,
               flex_direction="column",
               align_items="center",
               sizing_mode="stretch_width")
chart_collection[plot_key] = flex_obj

chart_collection["base_chart"] = get_base_chart()
