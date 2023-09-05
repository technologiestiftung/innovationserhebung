from abc import abstractmethod, ABC
from math import pi

from bokeh.models import ColumnDataSource, ColorBar
from bokeh.palettes import Category10, Category20c, Viridis256
from bokeh.plotting import figure
from bokeh.transform import cumsum, linear_cmap
import panel


PLOT_TYPES = {
    "bar": "BarPlotter",
    "bubble": "BubblePlotter",
    "line": "LinePlotter",
    "line_interactive": "InteractiveLinePlotter",
    "pie": "PiePlotter",
}


class PlotterFactory:
    @staticmethod
    def create_plotter(plot_type, raw_data, config):
        class_name = PLOT_TYPES[plot_type]
        cls = globals()[class_name]
        return cls(raw_data, config[plot_type])


class Plotter(ABC):
    def __init__(self, raw_data, config):
        self.raw_data = raw_data
        self.config = config
        self.fitted_data = None
        self.plot = None

    def generate(self):
        self.fit_data()
        self.create_plot()
        self.create_filters()

    @abstractmethod
    def fit_data(self):
        pass

    @abstractmethod
    def create_plot(self):
        pass

    def create_filters(self):
        pass


class BarPlotter(Plotter):
    def __init__(self, raw_data, config):
        # Create some example data
        super().__init__(raw_data, config)

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
    def __init__(self, raw_data, config):
        super().__init__(raw_data, config)

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
    def __init__(self, raw_data, config):
        super().__init__(raw_data, config)

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


class InteractiveLinePlotter(Plotter):
    def __init__(self, raw_data, config):
        super().__init__(raw_data, config)

        self.filters_multi_choice = None
        self.filters_single_choice_1 = None
        self.filters_single_choice_2 = None

    def fit_data(self):
        # Create initial data source
        single_choice_dict = (self.raw_data[self.config["filters"]["single_choice_1_default"]]
                                           [self.config["filters"]["single_choice_2_default"]])

        selected_lines = ["x"] + self.config["filters"]["multi_choice_default"]

        initial_data = {line: single_choice_dict[line]
                        for line in selected_lines}

        self.fitted_data = ColumnDataSource(initial_data)

    def create_plot(self):
        # Create a Bokeh figure
        self.plot = figure(**self.config["general"])

        # Add lines to the plot
        colors = Category10[10]
        for i, line_name in enumerate(self.config["filters"]["multi_choice"]):
            self.plot.line(x="x", y=line_name, source=self.fitted_data, color=colors[i], legend_label=line_name)

    def create_filters(self):
        # Create widgets
        self.filters_multi_choice = panel.widgets.CheckBoxGroup(
            name="Select branches",
            options=self.config["filters"]["multi_choice"],
            value=self.config["filters"]["multi_choice_default"]
        )

        self.filters_single_choice_1 = panel.widgets.RadioBoxGroup(
            name="Select unit", options=self.config["filters"]["single_choice_1"]
        )

        self.filters_single_choice_2 = panel.widgets.RadioBoxGroup(
            name="Select unit", options=self.config["filters"]["single_choice_2"]
        )

        # Add interactivity
        self.filters_multi_choice.param.watch(self.update_filters, "value")
        self.filters_single_choice_1.param.watch(self.update_filters, "value")
        self.filters_single_choice_2.param.watch(self.update_filters, "value")

    def update_filters(self, event):
        # Define the callback function for the filter
        selected_lines = self.filters_multi_choice.value
        single_choice_dict = self.raw_data[self.filters_single_choice_1.value][self.filters_single_choice_2.value]

        filtered_data = {
            "x": single_choice_dict["x"],
            **{line: single_choice_dict[line] for line in selected_lines}
        }

        # Update the existing ColumnDataSource with new data
        self.fitted_data.data = filtered_data


class PiePlotter(Plotter):
    def __init__(self, raw_data, config):
        super().__init__(raw_data, config)

    def fit_data(self):
        x_values = self.raw_data["x"]
        y_values = self.raw_data["y"]

        total = sum(y_values)
        angles = [2 * pi * (y / total) for y in y_values]
        colors = Category20c[len(x_values)]

        data = {
            "x": x_values,
            "y": y_values,
            "angle": angles,
            "color": colors,
        }

        source = ColumnDataSource(data)

        self.fitted_data = source

    def create_plot(self):
        plot = figure(**self.config["general"])

        plot.wedge(**self.config["wedge"],
                   source=self.fitted_data,
                   start_angle=cumsum("angle", include_zero=True),
                   end_angle=cumsum("angle"))
        plot.axis.axis_label = self.config["axis_label"]
        plot.axis.visible = self.config["visible"]
        plot.grid.grid_line_color = self.config["grid_line_color"]

        self.plot = plot
