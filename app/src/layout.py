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

chart_collection = {}
for plot_key in config:
    # Generate plots and filters
    plotter = plotter_factory.create_plotter(data[plot_key], config[plot_key])
    plotter.generate()

    # Place plots and filters in the layout
    flex_obj = FlexBox(*list(plotter.plots.values()),
                       *list(plotter.filters.values()),
                       flex_direction="column",
                       align_items="center",
                       sizing_mode="stretch_width")

    chart_collection[plot_key] = flex_obj
