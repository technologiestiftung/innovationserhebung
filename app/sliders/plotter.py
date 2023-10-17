from abc import abstractmethod, ABC
from math import pi

from bokeh.models import AnnularWedge, ColumnDataSource, ColorBar, Label
from bokeh.palettes import Category10, Category20c, Viridis256
from bokeh.plotting import figure
from bokeh.transform import cumsum, linear_cmap
import panel

import logging
logging.basicConfig(level=logging.INFO)

PLOT_TYPES = {
    "bar": "BarPlotter",
    "bubble": "BubblePlotter",
    "line": "LinePlotter",
    "line_interactive": "InteractiveLinePlotter",
    "pie": "PiePlotter",
    "pie_interactive": "InteractivePiePlotter",
}


class PlotterFactory:
    @staticmethod
    def create_plotter(plot_type, raw_data, config):
        """
        Create a plotter for a specific plot type.

        :param plot_type: str, type of plot
        :param raw_data: dict, data to plot
        :param config: dict, configuration for the plot
        :return: a plotter instance of the specified type
        """
        class_name = PLOT_TYPES[plot_type]
        cls = globals()[class_name]

        return cls(raw_data, config)


class Plotter(ABC):
    def __init__(self, raw_data, config):
        """
        Initialize a plotter.

        :param raw_data: dict, data to plot
        :param config: dict, default configuration
        """
        self.raw_data = raw_data
        self.config = config
        self.fitted_data = None
        self.plot = None

    def generate(self):
        """
        Run the necessary steps for creating a plot.
        """
        self.fit_data()
        self.create_plot()

    @abstractmethod
    def fit_data(self):
        """
        Prepare data.
        """
        pass

    @abstractmethod
    def create_plot(self):
        """
        Create plot.
        """
        pass


class InteractivePlotter(Plotter):
    def __init__(self, raw_data, config):
        super().__init__(raw_data, config)

    def generate(self):
        """
        Run the necessary steps for creating a plot.
        """
        self.fit_data()
        self.create_plot()
        self.create_filters()

    @abstractmethod
    def create_filters(self):
        """
        Create interactive filters.
        """
        pass

    @abstractmethod
    def update_filters(self, event):
        """
        Update data and plot whenever the user changes the filters.

        :param event: an event object that triggers the update
        """
        pass


class BarPlotter(Plotter):
    def __init__(self, raw_data, config):
        super().__init__(raw_data, config)

    def fit_data(self):
        self.fitted_data = ColumnDataSource(data=self.raw_data)

    def create_plot(self):
        # Create the figure
        self.plot = figure(x_range=self.fitted_data.data["x"], **self.config["general"])

        # Add vertical bars to the figure
        self.plot.vbar(x="x", top="y", source=self.fitted_data, **self.config["vbar"])

        # Show legends
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
        self.fitted_data = ColumnDataSource(data=self.raw_data)

    def create_plot(self):
        # Create the figure
        self.plot = figure(**self.config["general"])

        # Add a line glyph to the figure
        self.plot.line(x="x", y="y", source=self.fitted_data, **self.config["line"])

        # Show legends
        self.plot.legend.title = self.config["legend_title"]
        self.plot.legend.label_text_font_size = self.config["label_text_font_size"]


class InteractiveLinePlotter(InteractivePlotter):
    def __init__(self, raw_data, config):
        super().__init__(raw_data, config)

        self.filters_multi_choice = None
        self.filters_single_choice = None

    def fit_data(self):
        self.fitted_data = {}

        for code in self.config["plot_codes"]:
            # Extract data using the single choice filters
            single_choice_dict = (self.raw_data[code][self.config["filters"]["single_choice_default"]])

            # Get a subset of the lines selected with the multi choice filters
            selected_lines = ["x"] + self.config["filters"]["multi_choice_default"]
            initial_data = {line: single_choice_dict[line]
                            for line in selected_lines}

            self.fitted_data[code] = ColumnDataSource(initial_data)

    def create_plot(self):
        self.plot = {}

        for code in self.config["plot_codes"]:
            # Create a Bokeh figure
            self.plot[code] = figure(**self.config["general"])

            # Add lines to the plot
            colors = Category10[10]
            for i, line_name in enumerate(self.config["filters"]["multi_choice"]):
                self.plot[code].line(x="x", y=line_name, source=self.fitted_data[code], color=colors[i], legend_label=line_name)

    def create_filters(self):
        self.filters_single_choice = panel.widgets.RadioBoxGroup(
            name="Select unit", options=self.config["filters"]["single_choice"]
        )

        # Create multi choice filters
        self.filters_multi_choice = panel.widgets.CheckBoxGroup(
            name="Select branches",
            options=self.config["filters"]["multi_choice"],
            value=self.config["filters"]["multi_choice_default"]
        )

        # Add interactivity
        self.filters_multi_choice.param.watch(self.update_filters, "value")
        self.filters_single_choice.param.watch(self.update_filters, "value")

    def update_filters(self, event):
        for code in self.config["plot_codes"]:
            # Re select data based on new selection of filters
            selected_lines = self.filters_multi_choice.value
            single_choice_dict = self.raw_data[code][self.filters_single_choice.value]

            filtered_data = {
                "x": single_choice_dict["x"],
                **{line: single_choice_dict[line] for line in selected_lines}
            }

            # Update the existing ColumnDataSource with new data
            self.fitted_data[code].data = filtered_data


class PiePlotter(Plotter):
    def __init__(self, raw_data, config):
        super().__init__(raw_data, config)

    def fit_data(self):
        """
        Prepare data.
        """
        x_values = self.raw_data["x"]
        y_values = self.raw_data["y"]

        # Calculate area for each category in the pie chart
        total = sum(y_values)
        angles = [2 * pi * (y / total) for y in y_values]
        colors = Category20c[len(x_values)]

        # Transform data to the ColumDataSource format required by Bokeh
        data = {"x": x_values,
                "y": y_values,
                "angle": angles,
                "color": colors}
        source = ColumnDataSource(data)

        self.fitted_data = source

    def create_plot(self):
        # Create a Bokeh figure
        plot = figure(**self.config["general"])

        plot.wedge(**self.config["wedge"],
                   source=self.fitted_data,
                   start_angle=cumsum("angle", include_zero=True),
                   end_angle=cumsum("angle"))
        plot.axis.axis_label = self.config["axis_label"]
        plot.axis.visible = self.config["visible"]
        plot.grid.grid_line_color = self.config["grid_line_color"]

        self.plot = plot


class InteractivePiePlotter(InteractivePlotter):
    def __init__(self, raw_data, config):
        super().__init__(raw_data, config)

        self.filters_single_choice = None
        self.filters_single_choice_highlight = None
        self.center_labels = {}
        self.inner_rings = {}

    def fit_data(self):
        self.fitted_data = {}

        for code in self.config["plot_codes"]:
            # Extract data using the single choice filters
            single_choice_dict = (self.raw_data[code][self.config["filters"]["single_choice_default"]])

            # Get x and y values
            x_values = single_choice_dict["x"]
            y_values = single_choice_dict["y"]

            # Calculate area for each category in the pie chart
            total = sum(y_values)
            angles = [2 * pi * (y / total) for y in y_values]
            colors = Category20c[len(x_values)]

            # Transform data to the ColumnDataSource format required by Bokeh
            initial_data = {"x": x_values,
                            "y": y_values,
                            "angle": angles,
                            "color": colors}

            self.fitted_data[code] = ColumnDataSource(initial_data)

    def create_plot(self):
        self.plot = {}

        for code in self.config["plot_codes"]:
            # Create a Bokeh figure
            plot = figure(**self.config["general"])

            plot.annular_wedge(
                x=0,
                y=0,
                inner_radius=0.2,
                outer_radius=0.35,
                start_angle=cumsum("angle", include_zero=True),
                end_angle=cumsum("angle"),
                line_color=None,
                fill_color="color",
                legend_field="x",
                source=self.fitted_data[code],
            )

            # Add a label in the center
            highlight_category = self.config["filters"]["single_choice_highlight_default"]
            for key, value, color in zip(self.raw_data[code][self.config["filters"]["single_choice_default"]]["x"],
                                         self.raw_data[code][self.config["filters"]["single_choice_default"]]["y"],
                                         self.fitted_data[code].data["color"]):
                if key == highlight_category:
                    label_text = f"{str(value)} Mio €\n{highlight_category}"
                    highlight_color = color
                    break

            self.center_labels[code] = Label(
                x=0,
                y=0,
                text=label_text,
                text_align="center",
                text_baseline="middle",
                text_font_size="14pt",
            )

            plot.add_layout(self.center_labels[code])

            # Create an inner ring with the color of the highlighted category
            inner_radius = 0.17
            outer_radius = 0.21

            inner_ring = AnnularWedge(
                x=0,
                y=0,
                inner_radius=inner_radius,
                outer_radius=outer_radius,
                start_angle=0,
                end_angle=2*pi,
                line_color=None,
                fill_color=highlight_color,
            )

            self.inner_rings[code] = inner_ring
            plot.add_glyph(inner_ring)

            # Add other labels
            plot.axis.axis_label = self.config["axis_label"]
            plot.axis.visible = self.config["visible"]
            plot.grid.grid_line_color = self.config["grid_line_color"]

            self.plot[code] = plot

    def create_filters(self):
        # Create single choice filter
        self.filters_single_choice = panel.widgets.RadioButtonGroup(
            name="Select unit", options=self.config["filters"]["single_choice"]
        )

        # Create single choice highlight filter
        self.filters_single_choice_highlight = panel.widgets.RadioBoxGroup(
            name="Select unit", options=self.config["filters"]["single_choice_highlight"]
        )

        # Add interactivity
        self.filters_single_choice.param.watch(self.update_filters, "value")
        self.filters_single_choice_highlight.param.watch(self.update_filters, "value")

    def update_filters(self, event):
        for code in self.config["plot_codes"]:
            # Extract data using the single choice filters
            single_choice_dict = (self.raw_data[code][self.filters_single_choice.value])

            # Get x and y values
            x_values = single_choice_dict["x"]
            y_values = single_choice_dict["y"]

            # Calculate area for each category in the pie chart
            total = sum(y_values)
            angles = [2 * pi * (y / total) for y in y_values]
            colors = Category20c[len(x_values)]

            # Transform data to the ColumnDataSource format required by Bokeh
            filtered_data = {"x": x_values,
                             "y": y_values,
                             "angle": angles,
                             "color": colors}

            self.fitted_data[code].data = filtered_data

            # Update the center label to match the highlighted category
            highlight_category = self.filters_single_choice_highlight.value
            for key, value, color in zip(self.raw_data[code][self.filters_single_choice.value]["x"],
                                         self.raw_data[code][self.filters_single_choice.value]["y"],
                                         colors):
                if key == highlight_category:
                    self.center_labels[code].text = f"{str(value)} Mio €\n{highlight_category}"
                    self.inner_rings[code].fill_color = color
                    break
