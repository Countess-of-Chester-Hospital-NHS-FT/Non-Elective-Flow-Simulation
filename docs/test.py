import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os
import report_functions
import distribution_functions
root_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.append(root_dir)
from app.model import g, Trial
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import report_functions

mode=16
mean_list, std_list = distribution_functions.make_lognormal_lists(mode, 20)

df, fig, value_vars = report_functions.vary_demand(min_demand=36, max_demand=66, step=2, prop_sdec=0,
beds=456, losi=10, runs=10, escalation=0, reneging=0, prioritisation=0)

## alter which traces are visible
for trace in fig.data:
    trace.visible = False

desired_traces = {
    'ED Admissions': '#0066CC',     # Royal Blue
    'Daily 12hr DTAs': '#FF1493'    # Deep Pink
}
for trace in fig.data:
    trace.visible = trace.name in desired_traces
    if trace.visible:
        trace.line.color = desired_traces[trace.name]

max_demand = report_functions.find_max_demand(df, 'Daily 12hr DTAs')

fig.add_vline(
        x=max_demand,
        line_dash='dash',
        line_color='black',
        opacity=0.7
    )

fig.update_layout(
    title_text=f"Maximum theoretical demand for current beds and length of stay"
)

fig.show()

value_vars.insert(0, 'Demand')

df=df[value_vars]

df.set_index('Demand', inplace=True)
