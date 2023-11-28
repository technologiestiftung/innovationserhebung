import json

from panel.layout.flex import FlexBox

from app.importer.config_importer import ConfigImporter
from app.plot.plotter import PlotterFactory


# Load data
with open("app/data/outfile.json", "r") as f:
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
    flex_obj = FlexBox(
        *plotter.plots.values(),
        *plotter.filters.values(),
        flex_direction="column",
        align_items="center",
        sizing_mode="stretch_width",
    )

    chart_collection[plot_key] = flex_obj
