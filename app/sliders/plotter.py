from abc import abstractmethod, ABC
from math import pi

import pandas as pd

from bokeh.models import ColumnDataSource, ColorBar
from bokeh.palettes import Category10, Category20c, Viridis256
from bokeh.plotting import figure
from bokeh.transform import cumsum, linear_cmap
import panel

# TODO: Get rid of DF conversion as an intermediate step, following the interactive line plot example

PLOT_TYPES = {
    "bar": "BarPlotter",
    "bubble": "BubblePlotter",
    "line": "LinePlotter",
    "line_interactive": "InteractiveLinePlotter",
    "pie": "PiePlotter",
}


class PlotterFactory:
    @staticmethod
    def create_plotter(plot_type, raw_data):
        class_name = PLOT_TYPES[plot_type]
        cls = globals()[class_name]
        return cls(raw_data)


class Plotter(ABC):
    def __init__(self, raw_data):
        self.raw_data = raw_data  # TODO: Refactor so input is already a DF (comes from Importer)
        self.fitted_data = None
        self.plot = None
        self.config = None

    @abstractmethod
    def fit_data(self):
        pass

    @abstractmethod
    def create_plot(self):
        pass


class BarPlotter(Plotter):
    def __init__(self, raw_data):
        # Create some example data
        super().__init__(raw_data)

        config = {
            "general": {
                "title": "Simple Bar Chart",
                "x_axis_label": "Categories",
                "y_axis_label": "Values"
            },
            "vbar": {
                "width": 0.5,
                "legend_label": "Values",
                "line_color": "blue",
                "fill_color": "blue"
            },
            "legend_title": "Legend",
            "label_text_font_size": "12pt"
        }

        self.config = config

    def fit_data(self):
        self.fitted_data = ColumnDataSource(data=self.raw_data)

    def create_plot(self):
        # Create the figure
        self.plot = figure(x_range=self.fitted_data.data["x"], **self.config["general"])

        # Add vertical bars to the figure using the ColumnDataSource
        self.plot.vbar(x="x", top="y", source=self.fitted_data, **self.config["vbar"])

        # Show the legend
        self.plot.legend.title = self.config["legend_title"]
        self.plot.legend.label_text_font_size = self.config["label_text_font_size"]


class BubblePlotter(Plotter):
    def __init__(self, raw_data):
        super().__init__(raw_data)

        config = {
            "figure": {
                "title": "Simple Bubble Plot",
                "toolbar_location": None
            },
            "linear_cmap": {
                "field_name": "color",
                "palette": Viridis256
            },
            "circle": {
                "legend_field": "color"
            },
            "color_bar": {
                "width": 8,
                "location": (0, 0)
            }
        }

        self.config = config

    def fit_data(self):
        source = ColumnDataSource(data={"x": self.raw_data["x"],
                                        "y": self.raw_data["y"],
                                        "size": self.raw_data["size"],
                                        "color": self.raw_data["color"]})
        self.fitted_data = source

    def create_plot(self):
        # Create the figure
        self.plot = figure(**self.config["figure"])

        # Add circles to the plot
        mapper = linear_cmap(field_name="color", palette=Viridis256, low=min(self.fitted_data.data["color"]), high=max(self.fitted_data.data["color"]))
        self.plot.circle(x="x", y="y", size="size", color=mapper, source=self.fitted_data, **self.config["circle"])

        # Add color bar
        color_bar = ColorBar(color_mapper=mapper["transform"], **self.config["color_bar"])
        self.plot.add_layout(color_bar, "right")


class LinePlotter(Plotter):
    def __init__(self, raw_data):
        super().__init__(raw_data)

        config = {
            "general": {
                "title": "Simple Line Chart",
                "x_axis_label": "X-axis",
                "y_axis_label": "Y-axis"
            },
            "line": {
                "line_width": 2,
                "legend_label": "Line",
                "line_color": "blue"
            },
            "legend_title": "Legend",
            "label_text_font_size": "12pt"
        }

        self.config = config

    def fit_data(self):
        # Create a ColumnDataSource for the data
        self.fitted_data = ColumnDataSource(data=self.raw_data)

    def create_plot(self):
        # Create the figure
        self.plot = figure(**self.config["general"])

        # Add a line glyph to the figure
        self.plot.line(x="x", y="y", source=self.fitted_data, **self.config["line"])

        # Show the legend
        self.plot.legend.title = self.config["legend_title"]
        self.plot.legend.label_text_font_size = self.config["label_text_font_size"]


# TODO: Set a fixed scale so it doesn't shrink/grow automatically with updates
class InteractiveLinePlotter(Plotter):
    def __init__(self, raw_data):
        super().__init__(raw_data)

        config = {
            "general": {
                "title": "Interactive Line Chart",
                "x_axis_label": "X-axis",
                "y_axis_label": "Y-axis"
            },
            "line": {
                "line_width": 2,
                "legend_label": "Line",
                "line_color": "blue"
            },
            "legend_title": "Legend",
            "label_text_font_size": "12pt",
            "filters": {
                "single_choice": ["anzahl", "umsatz"],
                "single_choice_default": "anzahl",
                "multi_choice": ["nahrung", "pharma", "textil"],
                "multi_choice_default": ["nahrung", "pharma"]
            }
        }

        self.config = config

        self.filters_multi_choice = None
        self.filters_single_choice = None

    def fit_data(self):
        # Create widgets
        self.filters_multi_choice = panel.widgets.CheckBoxGroup(
            name="Select branches",
            options=self.config["filters"]["multi_choice"],
            value=self.config["filters"]["multi_choice_default"]
        )

        self.filters_single_choice = panel.widgets.RadioBoxGroup(
            name="Select unit", options=self.config["filters"]["single_choice"]
        )

        # Create initial data source
        keys = ["x"] + self.config["filters"]["multi_choice_default"]
        single_choice_dict = self.raw_data[self.config["filters"]["single_choice_default"]]
        initial_data = {k: single_choice_dict[k]
                        for k in keys}

        self.fitted_data = ColumnDataSource(initial_data)

    def create_plot(self):
        # TODO: Initial plot should be a subset of the multi choice
        #   and the boxes of those categories in the subset should be checked
        # Create a Bokeh figure
        self.plot = figure(**self.config["general"])

        # Add lines to the plot
        colors = Category10[10]
        for i, line_name in enumerate(self.config["filters"]["multi_choice"]):
            self.plot.line(x="x", y=line_name, source=self.fitted_data, color=colors[i], legend_label=line_name)

        # Add interactivity
        self.filters_multi_choice.param.watch(self.update, "value")
        self.filters_single_choice.param.watch(self.update, "value")

    def update(self, event):
        # Define the callback function for the filter
        selected_lines = self.filters_multi_choice.value
        single_choice_dict = self.raw_data[self.filters_single_choice.value]

        filtered_data = {
            "x": single_choice_dict["x"],
            **{line_name: single_choice_dict[line_name] for line_name in selected_lines}
        }

        # Update the existing ColumnDataSource with new data
        self.fitted_data.data = filtered_data


class PiePlotter(Plotter):
    def __init__(self, raw_data):
        super().__init__(raw_data)

        config = {
            "general": {
                "height": 350,
                "title": "Pie Chart",
                "toolbar_location": None,
                "tools": "hover",
                "tooltips": "@x: @y",
                "x_range": (-0.5, 1.0)
            },
            "wedge": {
                "x": 0,
                "y": 1,
                "radius": 0.4,
                "start_angle": cumsum("angle", include_zero=True),
                "end_angle": cumsum("angle"),
                "line_color": "white",
                "fill_color": "color",
                "legend_field": "x"
            },
            "axis_label": None,
            "visible": False,
            "grid_line_color": None
        }

        self.config = config

    def fit_data(self):

        df = pd.DataFrame(self.raw_data)
        df["angle"] = df["y"] / df["y"].sum() * 2 * pi
        df["color"] = Category20c[len(self.raw_data["x"])]

        source = ColumnDataSource(df)

        self.fitted_data = source

    def create_plot(self):
        plot = figure(**self.config["general"])

        plot.wedge(**self.config["wedge"], source=self.fitted_data)
        plot.axis.axis_label = self.config["axis_label"]
        plot.axis.visible = self.config["visible"]
        plot.grid.grid_line_color = self.config["grid_line_color"]

        self.plot = plot
