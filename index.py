from bokeh.layouts import gridplot, row, column
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from bokeh.embed import server_document
from bokeh.plotting import output_file, save
import panel as pn
from bokeh.models import Div, Tabs, TabPanel,GlobalImportedStyleSheet
from bokeh.themes import Theme
from question3 import question3_plot1, question3_plot2
from question4 import question4_plot1, question4_plot2, question4_plot3
from question12 import question1_1, question2_1, question2_2
import builtins
builtins.get_ipython = lambda: None  # Prevents errors in certain Jupyter environments

fig1, fig2 = question2_2()

plots = [
    question1_1(),
    question2_1(),
    fig1,
    fig2,
    question3_plot1(),
    question3_plot2(),
    question4_plot1(),
    question4_plot2(),
    question4_plot3()
]

# Dashboard Title
title = Div(
    text="<h1 style='text-align:center; margin:0; padding:0; font-family: Helvetica;'>Complete Reference for Dungeons and Dragons 5 Admin Dashboard</h1>",
    width=800, height=50
)

top_row = row(plots[0], plots[1])
bottom_row = row(plots[2], plots[3])
# bottom_row = gridplot([[fig1, fig2]],toolbar_location='right',merge_tools=True)
row1 = column(top_row, bottom_row)
# row1 = column(top_row, plots[2])
row2 = row(*plots[4:6])

row31 = row(*plots[6:8], width=750, height=500)
row32 = row(plots[8], width=750, height=500)
row3 = column(row31, row32)
# Tabs
tabs = Tabs(tabs=[
    TabPanel(child=row1, title="Sales"),
    TabPanel(child=row2, title="Crashes"),
    TabPanel(child=row3, title="Geographic"),
])

layout = [title, tabs]

output_file("index.html", title="Bokeh Dashboard")
save(layout)