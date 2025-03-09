from bokeh.layouts import gridplot
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from bokeh.embed import server_document
from bokeh.plotting import output_file, save
import panel as pn
from bokeh.models import Div
from question3 import question3_plot1, question3_plot2
from question4 import question4_plot1, question4_plot2
from question12 import question1_1, question2_1, question2_2

import builtins
builtins.get_ipython = lambda: None

fig1, fig2 = question2_2()

plots = [
    question1_1(),
    question2_1(),
    fig1,
    fig2,
    question3_plot1(),
    question3_plot2(),
    question4_plot1(),
    question4_plot2()
]

title = Div(
    text="<h1 style='text-align:center; color:#333; margin:0; padding:0;'>Complete Reference for Dungeons and Dragons 5 admin dashboard</h1>",
    width=800, height=50
)

background_style = """
    <style>
        body {
            background-color: red;  /* Light gray background */
        },
        .bk-root {
            background-color: red; /* White background for the Bokeh layout */
        }
    </style>
"""

style_div = Div(text=background_style, width=1, height=1)

layout = [title, style_div, gridplot([plots[:3], plots[3:6], plots[6:9], plots[9:12]],
                      sizing_mode="fixed",  # "scale_width" for auto-sizing
    width=650, height=350,
    toolbar_location="above",
    merge_tools=False
    )]


output_file("index.html", title="Bokeh Dashboard")

save(layout)