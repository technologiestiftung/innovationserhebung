from abc import abstractmethod, ABC
from math import pi

from bokeh.models import AnnularWedge, ColumnDataSource, Label
from bokeh.palettes import Category20, Category20c
from bokeh.plotting import figure
from bokeh.transform import cumsum, linear_cmap
import panel


PLOT_TYPES = {
    "bar_interactive": "InteractiveBarPlotter",
    "bubble_interactive": "InteractiveBubblePlotter",
    "line_interactive": "InteractiveLinePlotter",
    "pie_interactive": "InteractivePiePlotter",
}


class PlotterFactory:
    @staticmethod
    def create_plotter(raw_data, config):
        """
        Create a plotter for a specific plot type.

        :param raw_data: dict, raw_data to plot
        :param config: dict, configuration for the plot
        :return: a plotter instance of the specified type
        """
        class_name = PLOT_TYPES[config["plot_type"]]
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
        self.fitted_data = {}
        self.plots = {}

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

        self.filters = {}

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


class InteractiveBarPlotter(InteractivePlotter):
    def __init__(self, raw_data, config):
        super().__init__(raw_data, config)

    def fit_data(self):
        for code in self.config["plot_codes"]:
            for choice in self.config["filters"]["single_choice"]:
                for choice_2 in self.config["filters"]["single_choice_2"]:
                    x_values = self.raw_data[code][choice][choice_2]["x"]
                    # Define color palette
                    self.raw_data[code][choice][choice_2]["color"] = Category20[
                        len(x_values)
                    ]
                    # Split long x-axis in more than one line
                    for i, label in enumerate(x_values):
                        self.raw_data[code][choice][choice_2]["x"][i] = "/\n".join(
                            label.split("/")
                        )

        single_choice_default = self.config["filters_defaults"]["single_choice"]
        single_choice_2_default = self.config["filters_defaults"]["single_choice_2"]
        for code in self.config["plot_codes"]:
            single_choice_dict = self.raw_data[code][single_choice_default][
                single_choice_2_default
            ]

            self.fitted_data[code] = ColumnDataSource(data=single_choice_dict)

    def create_plot(self):
        for code in self.config["plot_codes"]:
            # Create the figure
            plot = figure(
                x_range=self.fitted_data[code].data["x"], **self.config["general"]
            )

            # Stretch to full width.
            plot.sizing_mode = "scale_width"
            plot.width_policy = "max"

            # Add vertical bars to the figure
            plot.vbar(
                x="x",
                top="y",
                source=self.fitted_data[code],
                color="color",
                **self.config["vbar"],
            )

            # Rotate x-axis labels
            plot.xaxis.major_label_orientation = pi / 2

            # Fixed line-height for tick-labels
            plot.xaxis.axis_label_text_line_height = 1

            self.plots[code] = plot

    def create_filters(self):
        # Create single choice filter
        self.filters["single_choice"] = panel.widgets.RadioBoxGroup(
            name="Select unit", options=self.config["filters"]["single_choice"]
        )

        # Create single choice highlight filter
        self.filters["single_choice_2"] = panel.widgets.RadioBoxGroup(
            name="Select unit", options=self.config["filters"]["single_choice_2"]
        )

        # Add interactivity
        self.filters["single_choice"].param.watch(self.update_filters, "value")
        self.filters["single_choice_2"].param.watch(self.update_filters, "value")

    def update_filters(self, event):
        for code in self.config["plot_codes"]:
            # Extract data using the single choice filters
            single_choice_dict = self.raw_data[code][
                self.filters["single_choice"].value
            ][self.filters["single_choice_2"].value]

            self.fitted_data[code].data = single_choice_dict


class InteractiveBubblePlotter(InteractivePlotter):
    def __init__(self, raw_data, config):
        super().__init__(raw_data, config)

    def fit_data(self):
        for code in self.config["plot_codes"]:
            single_choice_dict = self.raw_data[code][
                self.config["filters_defaults"]["single_choice"]
            ]
            source = ColumnDataSource(
                data={
                    "x": single_choice_dict["x"],
                    "y": single_choice_dict["y"],
                    "z": self.scale_values(single_choice_dict["z"]),
                    "color": [n for n in range(len(single_choice_dict["x"]))],
                    "labels": single_choice_dict["labels"],
                }
            )
            self.fitted_data[code] = source

    def create_plot(self):
        for code in self.config["plot_codes"]:
            # Get x and y range
            x_range = []
            y_range = []

            for key in self.config["filters"]["single_choice"]:
                x_range.extend(self.raw_data[code][key]["x"])
                y_range.extend(self.raw_data[code][key]["y"])

            # Create the figure
            plot = figure(
                **self.config["figure"],
                x_range=[min(x_range), max(x_range)],
                y_range=[min(y_range), max(y_range)],
            )

            # Add circles to the plot
            mapper = linear_cmap(
                field_name="color", palette=Category20[20], low=0, high=20
            )
            plot.circle(
                x="x",
                y="y",
                size="z",
                color=mapper,
                source=self.fitted_data[code],
                legend_group="labels",
            )

            # Set the position of the legend
            plot.add_layout(plot.legend[0], "right")

            self.plots[code] = plot

    def scale_values(self, values, threshold=150):
        """
        Helper function.
        Scale values of a list so that they don't exceed a maximum.

        :param values: list, containing integers
        :param max_value: int, maximum that the values shouldn't exceed
        :return: list, scaled values
        """
        max_val = max(values)
        scaling_factor = threshold / max_val if max_val > threshold else 1.0
        scaled_values = [x * scaling_factor for x in values]

        return scaled_values

    def create_filters(self):
        self.filters["single_choice"] = panel.widgets.RadioBoxGroup(
            name="Select unit", options=self.config["filters"]["single_choice"]
        )

        # Add interactivity
        self.filters["single_choice"].param.watch(self.update_filters, "value")

    def update_filters(self, event):
        for code in self.config["plot_codes"]:
            # Extract data using the single choice filter
            single_choice_dict = self.raw_data[code][
                self.filters["single_choice"].value
            ]
            data = {
                "x": single_choice_dict["x"],
                "y": single_choice_dict["y"],
                "z": self.scale_values(single_choice_dict["z"]),
                "color": [n for n in range(len(single_choice_dict["x"]))],
                "labels": single_choice_dict["labels"],
            }
            self.fitted_data[code].data = data


class InteractiveLinePlotter(InteractivePlotter):
    def __init__(self, raw_data, config):
        super().__init__(raw_data, config)

    def fit_data(self):
        for code in self.config["plot_codes"]:
            # Extract data using the single choice filters
            single_choice_dict = self.raw_data[code][
                self.config["filters_defaults"]["single_choice"]
            ]

            # Get a subset of the lines selected with the multi choice filters
            selected_lines = ["x"] + self.config["filters"]["multi_choice"]
            initial_data = {line: single_choice_dict[line] for line in selected_lines}

            self.fitted_data[code] = ColumnDataSource(initial_data)

    def create_plot(self):
        # Left-traverse nested data to get the x range
        x_range = self.raw_data
        while isinstance(x_range, dict):
            x_range = x_range[next(iter(x_range))]

        for code in self.config["plot_codes"]:
            # Create a Bokeh figure
            max_value = self.get_max_value(
                code, self.config["filters_defaults"]["single_choice"]
            )
            self.plots[code] = figure(
                **self.config["general"],
                x_range=[x_range[0], x_range[-1]],
                y_range=[0, max_value],
            )

            # Stretch to full width.
            self.plots[code].sizing_mode = "scale_width"
            self.plots[code].width_policy = "max"

            # Configure labels in x and y axes
            self.plots[code].xaxis.ticker = x_range
            self.plots[code].yaxis.formatter.use_scientific = False

            # Add lines to the plot
            colors = Category20[20]
            for i, line_name in enumerate(self.config["filters"]["multi_choice"]):
                self.plots[code].line(
                    x="x",
                    y=line_name,
                    source=self.fitted_data[code],
                    color=colors[i],
                    legend_label=line_name,
                )

    def create_filters(self):
        self.filters["single_choice"] = panel.widgets.RadioBoxGroup(
            name="Select unit", options=self.config["filters"]["single_choice"]
        )

        # Create multi choice filters
        self.filters["multi_choice"] = panel.widgets.CheckBoxGroup(
            name="Select branches",
            options=self.config["filters"]["multi_choice"],
            value=self.config["filters"]["multi_choice"],
        )

        # Add interactivity
        self.filters["multi_choice"].param.watch(self.update_filters, "value")
        self.filters["single_choice"].param.watch(self.update_filters, "value")
        self.filters["single_choice"].param.watch(self.update_y_range, "value")

    def update_filters(self, event):
        for code in self.config["plot_codes"]:
            # Re select data based on new selection of filters
            selected_lines = self.filters["multi_choice"].value
            single_choice_dict = self.raw_data[code][
                self.filters["single_choice"].value
            ]

            filtered_data = {
                "x": single_choice_dict["x"],
                **{line: single_choice_dict[line] for line in selected_lines},
            }

            # Update the existing ColumnDataSource with new data
            self.fitted_data[code].data = filtered_data

    def update_y_range(self, event):
        """
        Update y range when the user changes the single choice.

        :param event: an event object that triggers the update
        """
        for code in self.config["plot_codes"]:
            max_value = self.get_max_value(code, self.filters["single_choice"].value)
            self.plots[code].y_range.end = max_value

    def get_max_value(self, code, single_choice):
        """
        Helper function.

        :param code: str, code of the plot to modify
        :param single_choice: str, selected single choice
        :return: int | float, maximum value
        """
        all_values = []
        for key in self.config["filters"]["multi_choice"]:
            all_values.extend(self.raw_data[code][single_choice][key])
        max_value = max(all_values)

        return max_value


class InteractivePiePlotter(InteractivePlotter):
    def __init__(self, raw_data, config):
        super().__init__(raw_data, config)

        self.center_labels = {}
        self.center_labels_2nd_line = {}
        self.inner_rings = {}

    def fit_data(self):
        for code in self.config["plot_codes"]:
            # Extract data using the single choice filters
            single_choice_dict = self.raw_data[code][
                self.config["filters_defaults"]["single_choice"]
            ]

            # Get x and y values
            x_values = single_choice_dict["x"]
            y_values = single_choice_dict["y"]

            # Calculate area for each category in the pie chart
            total = sum(y_values)
            angles = [2 * pi * (y / total) for y in y_values]
            colors = Category20c[len(x_values)]

            # Transform data to the ColumnDataSource format required by Bokeh
            initial_data = {
                "x": x_values,
                "y": y_values,
                "angle": angles,
                "color": colors,
            }

            self.fitted_data[code] = ColumnDataSource(initial_data)

    def create_plot(self):
        single_choice_key = self.config["filters_defaults"]["single_choice"]
        highlight_category = self.config["filters_defaults"]["single_choice_highlight"]
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
            plot.sizing_mode = "scale_width"
            plot.width_policy = "max"

            # Add a label in the center
            for key, value, color in zip(
                self.raw_data[code][single_choice_key]["x"],
                self.raw_data[code][single_choice_key]["y"],
                self.fitted_data[code].data["color"],
            ):
                if key == highlight_category:
                    label_value = f"{str(int(value))} Mio €"
                    if len(highlight_category) > self.config["center_label_max_char"]:
                        label_text = (
                            highlight_category[: self.config["center_label_max_char"]]
                            + ".."
                        )
                    else:
                        label_text = highlight_category
                    highlight_color = color
                    break

            self.center_labels[code] = Label(
                x=0,
                y=0,
                text=label_value,
                text_align="center",
                text_baseline="middle",
                text_font_style="bold",
                y_offset=10,
                text_font_size="14pt",
            )

            plot.add_layout(self.center_labels[code])

            self.center_labels_2nd_line[code] = Label(
                x=0,
                y=0,
                text=label_text,
                text_align="center",
                text_baseline="middle",
                y_offset=-10,
                text_font_size="8pt",
            )

            plot.add_layout(self.center_labels_2nd_line[code])

            # Create an inner ring with the color of the highlighted category
            inner_radius = 0.17
            outer_radius = 0.21

            inner_ring = AnnularWedge(
                x=0,
                y=0,
                inner_radius=inner_radius,
                outer_radius=outer_radius,
                start_angle=0,
                end_angle=2 * pi,
                line_color=None,
                fill_color=highlight_color,
            )

            self.inner_rings[code] = inner_ring
            plot.add_glyph(inner_ring)

            # Add other labels
            plot.axis.axis_label = None
            plot.axis.visible = False
            plot.grid.grid_line_color = None

            self.plots[code] = plot

    def create_filters(self):
        # Create single choice filter
        self.filters["single_choice"] = panel.widgets.RadioButtonGroup(
            name="Select unit",
            options=self.config["filters"]["single_choice"],
            margin=(32, 0),
        )
        # Create single choice highlight filter
        self.filters["single_choice_highlight"] = panel.widgets.RadioBoxGroup(
            name="Select unit",
            options=self.config["filters"]["single_choice_highlight"],
        )

        # Add interactivity
        self.filters["single_choice"].param.watch(self.update_filters, "value")
        self.filters["single_choice_highlight"].param.watch(
            self.update_filters, "value"
        )

    def update_filters(self, event):
        for code in self.config["plot_codes"]:
            # Extract data using the single choice filters
            single_choice_dict = self.raw_data[code][
                self.filters["single_choice"].value
            ]

            # Get x and y values
            x_values = single_choice_dict["x"]
            y_values = single_choice_dict["y"]

            # Calculate area for each category in the pie chart
            total = sum(y_values)
            angles = [2 * pi * (y / total) for y in y_values]
            colors = Category20c[len(x_values)]

            # Transform data to the ColumnDataSource format required by Bokeh
            filtered_data = {
                "x": x_values,
                "y": y_values,
                "angle": angles,
                "color": colors,
            }

            self.fitted_data[code].data = filtered_data

            # Update the center label to match the highlighted category
            highlight_category = self.filters["single_choice_highlight"].value
            for key, value, color in zip(
                self.raw_data[code][self.filters["single_choice"].value]["x"],
                self.raw_data[code][self.filters["single_choice"].value]["y"],
                colors,
            ):
                if key == highlight_category:
                    self.center_labels[code].text = f"{str(int(value))} Mio €"
                    if len(highlight_category) > self.config["center_label_max_char"]:
                        self.center_labels_2nd_line[code].text = (
                            highlight_category[: self.config["center_label_max_char"]]
                            + ".."
                        )
                    else:
                        self.center_labels_2nd_line[code].text = highlight_category
                    self.inner_rings[code].fill_color = color
                    break
