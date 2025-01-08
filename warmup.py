import pandas as pd
import numpy as np
import plotly.express as px
from app.des_classes1 import g, Trial

#overwrite g class - so its easy to play around with
g.ed_inter_visit = (1440 / 38) # convert daily arrivals into inter-arrival time
g.sdec_inter_visit = (1440 / 11)
g.other_inter_visit = (1440 / 4)
g.number_of_nelbeds = 434
g.mean_time_in_bed = (225 * 60) # convert hrs to minutes
g.sd_time_in_bed = (405 * 60) # convert hrs to minutes
g.sim_duration = (120 * 24 * 60) # convert days into minutes
g.warm_up_period = (120 * 24 * 60)
g.number_of_runs = 8

# Call the run_trial method of our Trial object
all_event_logs, patient_df, patient_df_nowarmup, run_summary_df, trial_summary_df = Trial().run_trial()

#display(all_event_logs.head(1000))
display(patient_df.tail(1000))

#make chart for 1 run
#run1_df=patient_df[patient_df["run"]==0]
df=patient_df

#add a column called day
df["arrival_day"]=np.floor(df["arrival"]/1440)
display(df)

#average q_time_hrs by day
plot_df=df.groupby(["arrival_day", "run"]).agg(
    q_time_hrs=("q_time_hrs", "mean")
).reset_index()
#plot_df["rolling_mean"]=plot_df["q_time_hrs"].rolling(window=5).mean()
plot_df["rolling_qtime"]=(plot_df.groupby("run")["q_time_hrs"]
                         .transform(lambda x: x.rolling(window=5, min_periods=1)
                                    .mean()))
display(plot_df)

#plot
fig=px.line(plot_df, x="arrival_day", y="rolling_qtime", color="run")
fig.show()
