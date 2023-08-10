from math import pi

import numpy as np
import pandas as pd

from bokeh.models import ColumnDataSource, ColorBar
from bokeh.palettes import Category20c, Viridis256
from bokeh.plotting import figure
from bokeh.transform import cumsum, linear_cmap


# TODO: Clean and refactor, probably using the Factory Design Pattern
class PieChart:
    def __init__(self):

        x = {
            'United States': 157,
            'United Kingdom': 93,
            'Japan': 89,
            'China': 63,
            'Germany': 44,
            'India': 42,
            'Italy': 40,
            'Australia': 35,
            'Brazil': 32,
            'France': 31,
            'Taiwan': 31,
            'Spain': 29
        }

        data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'country'})
        data['angle'] = data['value'] / data['value'].sum() * 2 * pi
        data['color'] = Category20c[len(x)]

        self.plot = figure(height=350, title="Pie Chart", toolbar_location=None,
                           tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0))

        self.plot.wedge(x=0, y=1, radius=0.4,
                        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                        line_color="white", fill_color='color', legend_field='country', source=data)

        self.plot.axis.axis_label = None
        self.plot.axis.visible = False
        self.plot.grid.grid_line_color = None


class BubbleChart:
    def __init__(self):

        # Create some example data
        n = 20
        x = np.random.rand(n)
        y = np.random.rand(n)
        size = np.random.randint(10, 100, n)
        color = np.random.randint(0, 256, n)

        # Create a color mapper
        mapper = linear_cmap(field_name='color', palette=Viridis256, low=min(color), high=max(color))

        # Create a ColumnDataSource
        source = ColumnDataSource(data={'x': x, 'y': y, 'size': size, 'color': color})

        # Create the figure
        self.plot = figure(title='Simple Bubble Plot', toolbar_location=None)

        # Add circles to the plot
        self.plot.circle(x='x', y='y', size='size', color=mapper, source=source, legend_field='color')

        # Add color bar
        color_bar = ColorBar(color_mapper=mapper['transform'], width=8, location=(0, 0))
        self.plot.add_layout(color_bar, 'right')


class LineChart:
    def __init__(self):
        # Create some example data
        x = [1, 2, 3, 4, 5]
        y = [6, 7, 2, 4, 5]

        # Create the figure
        self.plot = figure(title='Simple Line Chart', x_axis_label='X-axis', y_axis_label='Y-axis')

        # Add a line glyph to the figure
        self.plot.line(x, y, line_width=2, legend_label='Line', line_color='blue')

        # Show the legend
        self.plot.legend.title = 'Legend'
        self.plot.legend.label_text_font_size = '12pt'


class BarChart:
    def __init__(self):
        # Create some example data
        categories = ['Category A', 'Category B', 'Category C', 'Category D']
        values = [15, 40, 25, 30]

        # Create the figure
        self.plot = figure(x_range=categories, title='Simple Bar Chart', x_axis_label='Categories', y_axis_label='Values')

        # Add vertical bars to the figure
        self.plot.vbar(x=categories, top=values, width=0.5, legend_label='Values', line_color='blue', fill_color='blue')

        # Show the legend
        self.plot.legend.title = 'Legend'
        self.plot.legend.label_text_font_size = '12pt'
