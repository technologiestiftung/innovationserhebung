import json

from panel.layout.flex import FlexBox
from panel.widgets import Select

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

    location_toggle = Select(options={
        'Deutschland': 'de', 'Berlin': 'ber'}, value='de')

    def create_update_chart(flex_obj, plotter):
        def update_chart(event):
            selected_location = event.new
            flex_obj.__setitem__(1, plotter.plots[selected_location])
        return update_chart

    # Place plots and filters in the layout
    flex_obj = FlexBox(location_toggle,
                       #    *plotter.plots.values(),
                       plotter.plots[location_toggle.value],
                       *plotter.filters.values(),
                       flex_direction="column",
                       align_items="center",
                       sizing_mode="stretch_width")

    update_chart = create_update_chart(flex_obj, plotter)
    location_toggle.param.watch(update_chart, 'value')

    chart_collection[plot_key] = flex_obj
