import json
import param

from panel.layout.gridstack import GridSpec
from panel.layout.flex import FlexBox
from panel.widgets import Select

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

with open("locales/de.json", "r") as f:
    content = json.load(f)

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
        plot_data = data["growth_bubble"]
    elif plot_key == "base_line_interactive":
        continue
    else:
        plot_data = data[plot_key]

    # TODO: Can refactor create_plotter() so I only need to pass the config as an argument
    plotter = plotter_factory.create_plotter(
        config[plot_key]["plot_type"], plot_data, config[plot_key])
    plotter.generate()

    plotters[plot_key] = plotter


def get_base_chart():
    # TODO: Import real data and adjust plotter accordingly
    interactive_line_plotter = plotter_factory.create_plotter("line_interactive",
                                                              data["base_line_interactive"],
                                                              config["base_line_interactive"])
    interactive_line_plotter.generate()

    line_plotter = plotter_factory.create_plotter(
        "line", line_data, config["base_line_interactive"])
    line_plotter.generate()

    select = Select(options={
        'Deutschland': 'de', 'Berlin': 'ber'}, value='de')

    plotted_base_charts = {
        'de': interactive_line_plotter.plot['de'],
        'ber': interactive_line_plotter.plot['ber'],
    }

    base_chart = GridSpec(sizing_mode="stretch_width", min_height=800)

    base_chart[0:1, 0:1] = select
    base_chart[1:8, 0:4] = plotted_base_charts[select.value]
    base_chart[8:12, 0:2] = interactive_line_plotter.filters_multi_choice
    base_chart[8:12, 2:4] = interactive_line_plotter.filters_single_choice

    def update_chart(event):
        selected_location = event.new
        base_chart[1:8, 0:4] = None
        base_chart[1:8, 0:4] = plotted_base_charts[selected_location]

    select.param.watch(update_chart, 'value')

    return base_chart


# TODO:
#  Think if I can simplify some of the code below, there is a lot of duplicate
#  Do we really need to use FlexBox AND GridSpec? Maybe we can just use one
chart_collection = {}

plot_key = "fue_pie_interactive"
plotter = plotters[plot_key]
plotted_charts = {
    'de': plotter.plot["de"],
    'ber': plotter.plot["ber"],
}

location_toggle = Select(options={
    'Deutschland': 'de', 'Berlin': 'ber'}, value='de')


flex_obj_1 = FlexBox(location_toggle,
                     plotted_charts[location_toggle.value],
                     plotter.filters_single_choice,
                     plotter.filters_single_choice_highlight,
                     flex_direction="column",
                     align_items="center",
                     sizing_mode="stretch_width")
chart_collection[plot_key] = flex_obj_1


def update_chart(event):
    selected_location = event.new
    flex_obj_1.__setitem__(1, plotted_charts[selected_location])


location_toggle.param.watch(update_chart, 'value')

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
flex_obj = FlexBox(plotter.plot["ber"],
                   plotter.plot["de"],
                   plotter.filters_single_choice,
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
