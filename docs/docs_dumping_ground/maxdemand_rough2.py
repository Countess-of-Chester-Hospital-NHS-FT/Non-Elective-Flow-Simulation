import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from app.model import g, Trial

g.ed_inter_visit = (1440 / 50) # convert daily arrivals into inter-arrival time
g.sdec_inter_visit = (1440 / 1)
g.other_inter_visit = (1440 / 1)
g.number_of_nelbeds = 434
g.mean_time_in_bed = (219 * 60) # convert hrs to minutes
g.sd_time_in_bed = (347 * 60) # convert hrs to minutes
g.sim_duration = (240 * 24 * 60) # convert days into minutes
g.warm_up_period = (120 * 24 * 60)
g.number_of_runs = 2

# Call the run_trial method of our Trial object
all_event_logs, patient_df, patient_df_nowarmup, run_summary_df, trial_summary_df = Trial().run_trial()

df = patient_df

patient_df_nowarmup = df[(df["arrival"] > g.warm_up_period) 
                         | (df["depart"] > g.warm_up_period)]