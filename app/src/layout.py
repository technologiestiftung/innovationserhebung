import json

from panel.layout.flex import FlexBox

from .config_importer import ConfigImporter
from .plotter import PlotterFactory


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
    plot_data = data[plot_key]

    # TODO: Can refactor create_plotter() so I only need to pass the config as an argument
    plotter = plotter_factory.create_plotter(config[plot_key]["plot_type"], plot_data, config[plot_key])
    plotter.generate()

    plotters[plot_key] = plotter


# TODO:
#  Think if I can simplify some of the code below, there is a lot of duplicate
chart_collection = {}

plot_key = "fue_pie_interactive"
plotter = plotters[plot_key]

flex_obj = FlexBox(plotter.plots["ber"],
                   plotter.plots["de"],
                   plotter.filters["single_choice"],
                   plotter.filters["single_choice_highlight"],
                   flex_direction="column",
                   align_items="center",
                   sizing_mode="stretch_width")
chart_collection[plot_key] = flex_obj

plot_key = "shares_pie_interactive"
plotter = plotters[plot_key]
flex_obj = FlexBox(plotter.plots["ber"],
                   plotter.plots["de"],
                   plotter.filters["single_choice"],
                   plotter.filters["single_choice_highlight"],
                   flex_direction="column",
                   align_items="center",
                   sizing_mode="stretch_width")
chart_collection[plot_key] = flex_obj

plot_key = "growth_bubble_interactive"
plotter = plotters[plot_key]
flex_obj = FlexBox(plotter.plots["ber"],
                   plotter.plots["de"],
                   plotter.filters["single_choice"],
                   flex_direction="column",
                   align_items="center",
                   sizing_mode="stretch_width")
chart_collection[plot_key] = flex_obj

plot_key = "coop_partner_bar_interactive"
plotter = plotters[plot_key]
flex_obj = FlexBox(plotter.plots["ber"],
                   plotter.filters["single_choice"],
                   plotter.filters["single_choice_2"],
                   flex_direction="column",
                   align_items="center",
                   sizing_mode="stretch_width")
chart_collection[plot_key] = flex_obj


plot_key = "base_line_interactive"
plotter = plotters[plot_key]
flex_obj = FlexBox(plotter.plots["ber"],
                   plotter.plots["de"],
                   plotter.filters["multi_choice"],
                   plotter.filters["single_choice"],
                   flex_direction="column",
                   align_items="center",
                   sizing_mode="stretch_width")
chart_collection[plot_key] = flex_obj
