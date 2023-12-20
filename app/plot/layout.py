from functools import lru_cache
import json

from panel.layout.flex import FlexBox
from panel.widgets import Select

from ..importer.config_importer import ConfigImporter
from .plotter import create_plotter


def update_chart(flex_obj, plotter):
    """
    Update chart on toggle selection by user.

    :param flex_obj: FlexBox object
    :param plotter: Plotter object
    :return: callable function
    """
    return lambda event: flex_obj.__setitem__(1, plotter.plots[event.new])


@lru_cache
def get_data():
    # Load data as dict
    with open("app/data/outfile.json", "r") as f:
        data = json.load(f)
    return data


@lru_cache
def get_config():
    # Get config as dict
    config_importer = ConfigImporter()
    return config_importer.get_config()


def get_flex_obj_fn_for_plot_key(plot_key):
    data = get_data()
    config = get_config()

    # Generate plots and filters
    plotter = create_plotter(data[plot_key], config[plot_key])
    plotter.generate()

    location_toggle = Select(
        options={"Deutschland": "de", "Berlin": "ber"}, value="ber"
    )

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

    return flex_obj.servable()


# Need to declare each function as is to be able to create the objects all separately


def base_line_interactive_app():
    return get_flex_obj_fn_for_plot_key("base_line_interactive")


def growth_bubble_interactive_app():
    return get_flex_obj_fn_for_plot_key("growth_bubble_interactive")


def shares_pie_interactive_app():
    return get_flex_obj_fn_for_plot_key("shares_pie_interactive")


def fue_pie_interactive_app():
    return get_flex_obj_fn_for_plot_key("fue_pie_interactive")


def coop_partner_bar_interactive_app():
    return get_flex_obj_fn_for_plot_key("coop_partner_bar_interactive")


def coop_region_bar_interactive_app():
    return get_flex_obj_fn_for_plot_key("coop_region_bar_interactive")


def protection_bar_interactive_app():
    return get_flex_obj_fn_for_plot_key("protection_bar_interactive")


def public_funding_bar_interactive_app():
    return get_flex_obj_fn_for_plot_key("public_funding_bar_interactive")


panels = {
    "base_line_interactive": base_line_interactive_app,
    "growth_bubble_interactive": growth_bubble_interactive_app,
    "shares_pie_interactive": shares_pie_interactive_app,
    "fue_pie_interactive": fue_pie_interactive_app,
    "coop_partner_bar_interactive": coop_partner_bar_interactive_app,
    "coop_region_bar_interactive": coop_region_bar_interactive_app,
    "protection_bar_interactive": protection_bar_interactive_app,
    "public_funding_bar_interactive": public_funding_bar_interactive_app,
}
