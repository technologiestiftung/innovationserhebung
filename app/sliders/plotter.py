from abc import abstractmethod, ABC
from math import pi

import pandas as pd

from bokeh.models import ColumnDataSource, ColorBar
from bokeh.palettes import Category20c, Viridis256
from bokeh.plotting import figure
from bokeh.transform import cumsum, linear_cmap


class Plotter(ABC):
    def __init__(self):
        self.data = None
        self.plot = None
        self.config = None

    @abstractmethod
    def fit_data(self, data):
        pass

    @abstractmethod
    def create_plot(self):
        pass


class PiePlotter(Plotter):
    def __init__(self):
        super().__init__()

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

    def fit_data(self, data):

        df = pd.DataFrame(data)
        df["angle"] = df["y"] / df["y"].sum() * 2 * pi
        df["color"] = Category20c[len(data["x"])]

        source = ColumnDataSource(df)

        self.data = source

    def create_plot(self):
        plot = figure(**self.config["general"])

        plot.wedge(**self.config["wedge"], source=self.data)
        plot.axis.axis_label = self.config["axis_label"]
        plot.axis.visible = self.config["visible"]
        plot.grid.grid_line_color = self.config["grid_line_color"]

        self.plot = plot


class BubblePlotter(Plotter):
    def __init__(self):
        super().__init__()

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

    def fit_data(self, data):
        source = ColumnDataSource(data={"x": data["x"],
                                        "y": data["y"],
                                        "size": data["size"],
                                        "color": data["color"]})
        self.data = source

    def create_plot(self):
        # Create the figure
        self.plot = figure(**self.config["figure"])

        # Add circles to the plot
        mapper = linear_cmap(field_name="color", palette=Viridis256, low=min(self.data.data["color"]), high=max(self.data.data["color"]))
        self.plot.circle(x="x", y="y", size="size", color=mapper, source=self.data, **self.config["circle"])

        # Add color bar
        color_bar = ColorBar(color_mapper=mapper["transform"], **self.config["color_bar"])
        self.plot.add_layout(color_bar, "right")


class LinePlotter(Plotter):
    def __init__(self):
        super().__init__()

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

    def fit_data(self, data):
        # Create a ColumnDataSource for the data
        self.data = ColumnDataSource(data=data)

    def create_plot(self):
        # Create the figure
        self.plot = figure(**self.config["general"])

        # Add a line glyph to the figure
        self.plot.line(x="x", y="y", source=self.data, **self.config["line"])

        # Show the legend
        self.plot.legend.title = self.config["legend_title"]
        self.plot.legend.label_text_font_size = self.config["label_text_font_size"]


class BarPlotter(Plotter):
    def __init__(self):
        # Create some example data
        super().__init__()

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

    def fit_data(self, data):
        self.data = ColumnDataSource(data=data)

    def create_plot(self):
        # Create the figure
        self.plot = figure(x_range=self.data.data["x"], **self.config["general"])

        # Add vertical bars to the figure using the ColumnDataSource
        self.plot.vbar(x="x", top="y", source=self.data, **self.config["vbar"])

        # Show the legend
        self.plot.legend.title = self.config["legend_title"]
        self.plot.legend.label_text_font_size = self.config["label_text_font_size"]


class PlotterFactory:
    @staticmethod
    def create_plotter(plot_type):
        class_name = plot_type.capitalize() + "Plotter"
        cls = globals()[class_name]
        return cls()
