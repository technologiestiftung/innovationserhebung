import panel as pn
from panel.layout.gridstack import GridSpec

from .plotters import BarChart, BubbleChart, LineChart, SineWave, PieChart


def createApp():
    pc = PieChart()
    pc2 = PieChart()
    sw = SineWave()
    bc = BubbleChart()
    lc = LineChart()
    bac = BarChart()

    gspec = GridSpec(width=800, height=1000)

    gspec[0:1, 0:1] = pc.plot
    gspec[0:1, 1:2] = pc2.plot
    gspec[1:2, 0:2] = sw.plot
    gspec[2:3, 0:2] = bc.plot
    gspec[3:4, 0:2] = lc.plot
    gspec[4:5, 0:2] = bac.plot

    return gspec.servable()
