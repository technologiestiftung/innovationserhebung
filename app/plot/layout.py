import json

from panel.layout.flex import FlexBox
from panel.widgets import Select

from ..importer.config_importer import ConfigImporter
from .plotter import create_plotter


# Load data
with open("app/data/outfile.json", "r") as f:
    data = json.load(f)

# Load config
config_importer = ConfigImporter()
config = config_importer.get_config()

# Initialize plotter factory
chart_collection = {}


def update_chart(flex_obj, plotter):
    """
    Update chart on toggle selection by user.

    :param flex_obj: FlexBox object
    :param plotter: Plotter object
    :return: callable function
    """
    return lambda event: flex_obj.__setitem__(1, plotter.plots[event.new])


for plot_key in config:
    # Generate plots and filters
    plotter = create_plotter(data[plot_key], config[plot_key])
    plotter.generate()

    location_toggle = Select(options={"Deutschland": "de", "Berlin": "ber"}, value="de")

    # Place plots and filters in the layout
    flex_obj = FlexBox(
        location_toggle,
        #    *plotter.plots.values(),
        plotter.plots[location_toggle.value],
        *plotter.filters.values(),
        flex_direction="column",
        align_items="center",
        sizing_mode="stretch_width",
    )

    # Connect toggle to the show display so that it changes on user selection
    location_toggle.param.watch(update_chart(flex_obj, plotter), "value")

    chart_collection[plot_key] = flex_obj
