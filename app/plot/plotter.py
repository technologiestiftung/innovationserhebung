from abc import abstractmethod, ABC
from math import pi

from bokeh.models import ColumnDataSource, Label, HoverTool
from bokeh.plotting import figure
from bokeh.transform import cumsum, linear_cmap
import panel
from panel.layout.accordion import Accordion

import logging

logging.basicConfig(level=logging.INFO)


PLOT_TYPES = {
    "bar_interactive": "InteractiveBarPlotter",
    "bubble_interactive": "InteractiveBubblePlotter",
    "line_interactive": "InteractiveLinePlotter",
    "pie_interactive": "InteractivePiePlotter",
}

custom_palette = [
    "#6CB2E0",
    "#EE4C70",
    "#41B496",
    "#E7EA81",
    "#B1B2B3",
    "#99DCF8",
    "#B2D9A8",
    "#7ACBB5",
    "#DCC82D",
    "#6ECDF5",
    "#5BB5B5",
    "#6273B2",
    "#E60032",
    "#2D91D2",
    "#B2D9A8",
    "#EADE81",
    "#1E3791",
    "#5BB5B5",
    "#6F6F6E",
]


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
                    self.raw_data[code][choice][choice_2]["color"] = custom_palette[
                        : len(x_values)
                    ]

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
            x_range = self.fitted_data[code].data["x"]
            plot = figure(x_range=x_range, **self.config["general"])

            # Stretch to full width.
            plot.sizing_mode = "scale_width"
            plot.width_policy = "max"

            # Change background color
            plot.background_fill_color = self.config["background_fill_color"]
            plot.border_fill_color = self.config["background_fill_color"]
            plot.outline_line_color = self.config["background_fill_color"]

            # Hide x grid
            plot.xgrid.grid_line_color = None

            # # Configure axes
            plot.yaxis.ticker.desired_num_ticks = 8
            plot.yaxis.minor_tick_line_color = None
            plot.yaxis.formatter.use_scientific = False
            plot.yaxis.axis_label_text_color = "#878786"

            for axis in [plot.xaxis, plot.yaxis]:
                axis.major_tick_line_color = None
                axis.axis_label_text_font = self.config["text"]["font"]
                axis.axis_label_text_font_style = self.config["text"]["font_style"]
                axis.axis_label_text_font_size = "13px"
                axis.major_label_text_font = self.config["text"]["font"]
                axis.major_label_text_color = "#878786"
                axis.major_label_text_font_style = self.config["text"]["font_style"]
                axis.axis_line_width = self.config["axis"]["axis_line_width"]
                axis.axis_line_color = self.config["background_fill_color"]
                axis.axis_label_text_color = "#3B3B3A"

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
        self.filters["single_choice"] = panel.widgets.RadioButtonGroup(
            name="Select unit",
            options=self.config["filters"]["single_choice"],
            margin=(32, 0),
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

            # Add tooltip categories
            n = len(single_choice_dict["x"])
            tooltip_cat_1_list = [self.config["tooltip"]["tooltip_cat_1"]] * n
            tooltip_cat_2_list = [self.config["tooltip"]["tooltip_cat_2"]] * n
            source = ColumnDataSource(
                data={
                    "x": single_choice_dict["x"],
                    "y": single_choice_dict["y"],
                    "z": self.scale_values(single_choice_dict["z"]),
                    "color": [n for n in range(len(single_choice_dict["x"]))],
                    "labels": single_choice_dict["labels"],
                    "tooltip_cat_1": tooltip_cat_1_list,
                    "tooltip_cat_2": tooltip_cat_2_list,
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
                **self.config["general"],
                x_range=[min(x_range), max(x_range)],
                y_range=[min(y_range), max(y_range)],
            )

            tooltip_html = """
                <div style="padding: .5rem; display: flex; flex-direction: column; ">
                    <div style="font-size: 1rem; font-weight: bold;">
                        <strong>@labels</strong>
                    </div>
                    <div style="font-size: 1rem; display:flex; justify-content: space-between; margin-top: 1rem; align-items: center; gap:2rem; width: 100%;">
                        <p style="color: #878786; margin: 0;">@tooltip_cat_1:</p>
                        <strong>@y Mio. €</strong>
                    </div>
                    <div style="font-size: 1rem; display:flex; justify-content: space-between; align-items: center; gap:2rem; width: 100%;">
                        <p style="color: #878786; margin: 0;">@tooltip_cat_2:</p>
                        <strong>@z Tsd.</strong>
                    </div>
                </div>
            """

            hover_tool = HoverTool(
                tooltips=tooltip_html,
                attachment="above",
                line_policy="nearest",
                point_policy="snap_to_data",
                anchor="center_right",
            )

            plot.sizing_mode = "scale_width"
            plot.width_policy = "max"
            plot.add_tools(hover_tool)

            # Change background color
            plot.background_fill_color = self.config["background_fill_color"]
            plot.border_fill_color = self.config["background_fill_color"]
            plot.outline_line_color = self.config["background_fill_color"]

            # Hide x grid
            plot.xgrid.grid_line_color = None

            # # Configure axes
            plot.yaxis.ticker.desired_num_ticks = 8
            plot.yaxis.formatter.use_scientific = False
            plot.yaxis.axis_label_text_color = "#878786"

            for axis in [plot.xaxis, plot.yaxis]:
                axis.minor_tick_line_color = None
                axis.major_tick_line_color = None
                axis.axis_label_text_font = self.config["text"]["font"]
                axis.axis_label_text_font_style = self.config["text"]["font_style"]
                axis.axis_label_text_font_size = "13px"
                axis.major_label_text_font = self.config["text"]["font"]
                axis.major_label_text_color = "#878786"
                axis.major_label_text_font_style = self.config["text"]["font_style"]
                axis.axis_line_width = self.config["axis"]["axis_line_width"]
                axis.axis_line_color = self.config["background_fill_color"]
                axis.axis_label_text_color = "#3B3B3A"

            # Add circles to the plot
            mapper = linear_cmap(
                field_name="color",
                palette=custom_palette[: len(x_range)],
                low=0,
                high=20,
            )
            plot.circle(
                x="x",
                y="y",
                size="z",
                color=mapper,
                source=self.fitted_data[code],
            )

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
        self.filters["single_choice"] = panel.widgets.RadioButtonGroup(
            name="Select unit",
            options=self.config["filters"]["single_choice"],
            margin=(32, 0),
            css_classes=["single_choice_toggle"],
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
                x_range=[x_range[0] - 0.25, x_range[-1] + 0.25],
                y_range=[0, max_value],
            )

            # Stretch to full width.
            self.plots[code].sizing_mode = "scale_width"
            self.plots[code].width_policy = "max"

            # Change background color
            self.plots[code].background_fill_color = self.config[
                "background_fill_color"
            ]
            self.plots[code].border_fill_color = self.config["background_fill_color"]
            self.plots[code].outline_line_color = self.config["background_fill_color"]

            # Hide x grid
            self.plots[code].xgrid.grid_line_color = None

            # Configure axes
            self.plots[code].xaxis.ticker = x_range
            self.plots[code].yaxis.ticker.desired_num_ticks = 8
            self.plots[code].yaxis.minor_tick_line_color = None
            self.plots[code].yaxis.formatter.use_scientific = False
            self.plots[code].yaxis.axis_label_text_color = "#878786"

            for axis in [self.plots[code].xaxis, self.plots[code].yaxis]:
                axis.major_tick_line_color = None
                axis.axis_label_text_font = self.config["text"]["font"]
                axis.axis_label_text_font_style = self.config["text"]["font_style"]
                axis.axis_label_text_font_size = "13px"
                axis.major_label_text_font = self.config["text"]["font"]
                axis.major_label_text_color = "#878786"
                axis.major_label_text_font_style = self.config["text"]["font_style"]
                axis.axis_line_width = self.config["axis"]["axis_line_width"]
                axis.axis_line_color = self.config["background_fill_color"]
                axis.axis_label_text_color = "#3B3B3A"

            # Add lines to the plot
            colors = custom_palette
            for i, line_name in enumerate(self.config["filters"]["multi_choice"]):
                self.plots[code].line(
                    x="x",
                    y=line_name,
                    source=self.fitted_data[code],
                    color=colors[i],
                    line_width=4,
                )
                self.plots[code].circle(
                    x="x",
                    y=line_name,
                    source=self.fitted_data[code],
                    color=colors[i],
                    size=16,
                )
                self.plots[code].circle(
                    x="x",
                    y=line_name,
                    source=self.fitted_data[code],
                    color=self.config["background_fill_color"],
                    size=12,
                )

    def create_filters(self):
        filters_single_choice = panel.widgets.RadioBoxGroup(
            name="Select unit", options=self.config["filters"]["single_choice"]
        )

        filters_multi_choice = panel.Column(
            *[
                panel.Row(
                    panel.pane.HTML(
                        '<div class="legend-field" style="background-color:{};"></div>'.format(
                            color
                        )
                    ),
                    panel.widgets.Checkbox(
                        name=option, value=True, css_classes=["legend-checkbox"]
                    ),
                )
                for color, option in zip(
                    custom_palette, self.config["filters"]["multi_choice"]
                )
            ]
        )

        filter_options = {
            "header_color": self.config["corporate_text_color"],
            "active_header_background": self.config["background_fill_color"],
            "header_background": self.config["background_fill_color"],
        }
        self.filters["multi_choice"] = Accordion(
            ("Branchen auswählen", filters_multi_choice), active=[0], **filter_options
        )
        self.filters["single_choice"] = Accordion(
            ("Einheiten auswählen", filters_single_choice), **filter_options
        )

        # Add interactivity
        for filter_row in self.filters["multi_choice"][0]:
            filter_row[1].param.watch(self.update_filters, "value")
        self.filters["single_choice"][0].param.watch(self.update_filters, "value")
        self.filters["single_choice"][0].param.watch(self.update_y_range, "value")

    def update_filters(self, event):
        # TODO: Update filters
        for code in self.config["plot_codes"]:
            selected_lines = []
            # Re select data based on new selection of filters
            for filter_row in self.filters["multi_choice"][0]:
                if filter_row[1].value:
                    selected_lines.append(filter_row[1].name)
            single_choice_dict = self.raw_data[code][
                self.filters["single_choice"][0].value
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
            max_value = self.get_max_value(code, self.filters["single_choice"][0].value)
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

            # Transform data to the ColumnDataSource format required by Bokeh
            initial_data = {
                "x": x_values,
                "y": y_values,
                "angle": angles,
                "color": custom_palette[: len(x_values)],
            }

            self.fitted_data[code] = ColumnDataSource(initial_data)

    def create_plot(self):
        highlight_category = self.config["filters_defaults"]["single_choice_highlight"]
        for code in self.config["plot_codes"]:
            tooltip_html = """
                <div style="padding: .5rem;">
                    <div style="font-size: 1rem; font-weight: bold;">
                        <strong>@x</strong>
                    </div>
                    <div style="font-size: 1rem; display:flex; justify-content: space-between; align-items: center; gap:2rem; width: 100%;">
                        <p style="color: #878786;">insgesamt:</p>
                        <strong>@y Mio. €</strong>
                    </div>
                </div>
            """

            hover_tool = HoverTool(
                tooltips=tooltip_html,
                attachment="above",
                line_policy="nearest",
                point_policy="snap_to_data",
                anchor="center_right",
            )
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
                source=self.fitted_data[code],
            )

            plot.sizing_mode = "scale_width"
            plot.width_policy = "max"

            # Change background color
            plot.background_fill_color = self.config["background_fill_color"]
            plot.border_fill_color = self.config["background_fill_color"]
            plot.outline_line_color = self.config["background_fill_color"]
            plot.add_tools(hover_tool)

            # Add a label in the center
            highlight_category = self.config["filters_defaults"][
                "single_choice_highlight"
            ]
            for key, value, color in zip(
                self.raw_data[code][self.config["filters_defaults"]["single_choice"]][
                    "x"
                ],
                self.raw_data[code][self.config["filters_defaults"]["single_choice"]][
                    "y"
                ],
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
                    break

            self.center_labels[code] = Label(
                x=0,
                y=0,
                text=label_value,
                # text=label_value,
                text_align="center",
                text_baseline="middle",
                text_font_style="bold",
                y_offset=10,
                text_font_size="14pt",
            )

            self.center_labels_2nd_line[code] = Label(
                x=0,
                y=0,
                text=label_text,
                text_align="center",
                text_baseline="middle",
                y_offset=-10,
                text_font_size="8pt",
            )

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
        self.filters["single_choice"].param.watch(self.update_filters, "value")

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

            # Transform data to the ColumnDataSource format required by Bokeh
            filtered_data = {
                "x": x_values,
                "y": y_values,
                "angle": angles,
                "color": custom_palette[: len(x_values)],
            }

            self.fitted_data[code].data = filtered_data
