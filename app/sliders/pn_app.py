import json

from panel.layout.accordion import Accordion
from panel.layout.flex import FlexBox
from panel.widgets import Select

from .config_importer import ConfigImporter
from .plotter import PlotterFactory

import logging
logging.basicConfig(level=logging.INFO)

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

# Use de.json as source of chart ids and toggle texts
with open("locales/de.json", "r") as f:
    content = json.load(f)

# allCharts = []

# for section in content["sections"]:
#     if section["type"] == "chart":
#         charts = section["charts"]
#         for chart in charts:
#             if chart["id"]:
#                 chart_obj = {
#                     "chartId": chart["id"],
#                     "toggleText": chart["toggleText"]
#                 }
#                 allCharts.append(chart_obj)


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
    plotter = plotter_factory.create_plotter("line_interactive",
                                             data["base_line_interactive"],
                                             config["base_line_interactive"])
    plotter.generate()

    line_plotter = plotter_factory.create_plotter(
        "line", line_data, config["base_line_interactive"])
    line_plotter.generate()

    location_toggle = Select(options={
        'Deutschland': 'de', 'Berlin': 'ber'}, value='de')

    filters_multi_choice_accordion = Accordion(
        ("Branchen auswählen", plotter.filters_multi_choice), header_color="#1E3791", active_header_background="#F6F6F6", header_background="#F6F6F6")
    filters_single_choice_accordion = Accordion(
        ("Einheiten auswählen", plotter.filters_single_choice), header_color="#1E3791", active_header_background="#F6F6F6", header_background="#F6F6F6")

    flex_obj = FlexBox(location_toggle,
                       plotter.plot[location_toggle.value],
                       filters_multi_choice_accordion,
                       filters_single_choice_accordion,
                       flex_direction="column",
                       align_items="center",
                       sizing_mode="stretch_width")

    update_chart = create_update_chart(flex_obj, plotter)
    location_toggle.param.watch(update_chart, 'value')

    return flex_obj


# TODO:
#  Think if I can simplify some of the code below, there is a lot of duplicate

def create_update_chart(flex_obj, plotter):
    def update_chart(event):
        selected_location = event.new
        flex_obj.__setitem__(1, plotter.plot[selected_location])
    return update_chart


chart_collection = {}


plot_key = "fue_pie_interactive"
plotter = plotters[plot_key]
location_toggle = Select(options={
    'Deutschland': 'de', 'Berlin': 'ber'}, value='de')

flex_obj = FlexBox(location_toggle,
                   plotter.plot[location_toggle.value],
                   plotter.filters_single_choice,
                   plotter.filters_single_choice_highlight,
                   flex_direction="column",
                   align_items="center",
                   sizing_mode="stretch_width")
chart_collection[plot_key] = flex_obj


update_chart = create_update_chart(flex_obj, plotter)
location_toggle.param.watch(update_chart, 'value')


location_toggle = Select(options={
    'Deutschland': 'de', 'Berlin': 'ber'}, value='de')

plot_key = "shares_pie_interactive"
plotter = plotters[plot_key]
flex_obj = FlexBox(location_toggle,
                   plotter.plot[location_toggle.value],
                   plotter.filters_single_choice,
                   plotter.filters_single_choice_highlight,
                   flex_direction="column",
                   align_items="center",
                   sizing_mode="stretch_width")
chart_collection[plot_key] = flex_obj

update_chart = create_update_chart(flex_obj, plotter)
location_toggle.param.watch(update_chart, 'value')


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
