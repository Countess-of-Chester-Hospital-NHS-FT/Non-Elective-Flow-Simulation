import pandas as pd
import numpy as np
import plotly.express as px
from app.model import g, Trial

############################ default scenario ###################################
print("Plots for default scenario")
#overwrite g class - so its easy to play around with
g.ed_inter_visit = (1440 / 39) # convert daily arrivals into inter-arrival time
g.sdec_inter_visit = (1440 / 11)
g.other_inter_visit = (1440 / 3)
g.number_of_nelbeds = 434
g.mean_time_in_bed = (219 * 60) # convert hrs to minutes
g.sd_time_in_bed = (347 * 60) # convert hrs to minutes
g.sim_duration = (240 * 24 * 60) # convert days into minutes
g.warm_up_period = (120 * 24 * 60)
g.number_of_runs = 10

# Call the run_trial method of our Trial object
all_event_logs, patient_df, patient_df_nowarmup, run_summary_df, trial_summary_df = Trial().run_trial()

df=patient_df

#add a column called arrival day
df["arrival_day"]=np.floor(df["arrival"]/1440)
#display(df)

#average q_time_hrs by day
plot_df=df.groupby(["arrival_day", "run"]).agg(
    q_time_hrs=("q_time_hrs", "mean"),
    med_hrs=("q_time_hrs", "median"),
    reneged=("renege", "count"),
    max_hrs=("q_time_hrs", "max"),
    p95_hrs=("q_time_hrs", lambda x: np.nanpercentile(x, 95)),
    dtas=("q_time_hrs", lambda x: (x > 12).sum()),
    perf=("q_time_hrs", lambda x: (x < 4).sum() / x.count() * 100)
).reset_index()

#display(plot_df)
#calculate rolling average by day
plot_df["rolling_qtime"]=(plot_df.groupby("run")["q_time_hrs"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_med"]=(plot_df.groupby("run")["med_hrs"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_reneged"]=(plot_df.groupby("run")["reneged"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_max"]=(plot_df.groupby("run")["max_hrs"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_p95"]=(plot_df.groupby("run")["p95_hrs"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_dtas"]=(plot_df.groupby("run")["dtas"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_perf"]=(plot_df.groupby("run")["perf"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
#display(plot_df)

#plot mean q time
fig=px.line(plot_df, x="arrival_day", y="rolling_qtime", color="run")
fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(fig.show())

fig=px.line(plot_df, x="arrival_day", y="rolling_med", color="run")
fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(fig.show())

#plot daily reneged
r_fig=px.line(plot_df, x="arrival_day", y="rolling_reneged", color="run")
r_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(r_fig.show())

max_fig=px.line(plot_df, x="arrival_day", y="rolling_max", color="run")
max_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(max_fig.show())

max_fig=px.line(plot_df, x="arrival_day", y="rolling_p95", color="run")
max_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(max_fig.show())

max_fig=px.line(plot_df, x="arrival_day", y="rolling_dtas", color="run")
max_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(max_fig.show())

max_fig=px.line(plot_df, x="arrival_day", y="rolling_perf", color="run")
max_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(max_fig.show())

############################ worst flow scenario ###################################
print("Plots for worst flow scenario")
#overwrite g class - so its easy to play around with
g.ed_inter_visit = (1440 / 55) # convert daily arrivals into inter-arrival time
g.sdec_inter_visit = (1440 / 30)
g.other_inter_visit = (1440 / 3)
g.number_of_nelbeds = 380
g.mean_time_in_bed = (300 * 60) # convert hrs to minutes
g.sd_time_in_bed = (347 * 60) # convert hrs to minutes
g.sim_duration = (240 * 24 * 60) # convert days into minutes
g.warm_up_period = (120 * 24 * 60)
g.number_of_runs = 5

# Call the run_trial method of our Trial object
all_event_logs, patient_df, patient_df_nowarmup, run_summary_df, trial_summary_df = Trial().run_trial()

df=patient_df

#add a column called arrival day
df["arrival_day"]=np.floor(df["arrival"]/1440)
#display(df)

#average q_time_hrs by day
plot_df=df.groupby(["arrival_day", "run"]).agg(
    q_time_hrs=("q_time_hrs", "mean"),
    med_hrs=("q_time_hrs", "median"),
    reneged=("renege", "count"),
    max_hrs=("q_time_hrs", "max"),
    p95_hrs=("q_time_hrs", lambda x: np.nanpercentile(x, 95)),
    dtas=("q_time_hrs", lambda x: (x > 12).sum()),
    perf=("q_time_hrs", lambda x: (x < 4).sum() / x.count() * 100)
).reset_index()

#display(plot_df)
#calculate rolling average by day
plot_df["rolling_qtime"]=(plot_df.groupby("run")["q_time_hrs"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_med"]=(plot_df.groupby("run")["med_hrs"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_reneged"]=(plot_df.groupby("run")["reneged"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_max"]=(plot_df.groupby("run")["max_hrs"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_p95"]=(plot_df.groupby("run")["p95_hrs"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_dtas"]=(plot_df.groupby("run")["dtas"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_perf"]=(plot_df.groupby("run")["perf"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
#display(plot_df)

#plot mean q time
fig=px.line(plot_df, x="arrival_day", y="rolling_qtime", color="run")
fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(fig.show())

fig=px.line(plot_df, x="arrival_day", y="rolling_med", color="run")
fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(fig.show())

#plot daily reneged
r_fig=px.line(plot_df, x="arrival_day", y="rolling_reneged", color="run")
r_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(r_fig.show())

max_fig=px.line(plot_df, x="arrival_day", y="rolling_max", color="run")
max_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(max_fig.show())

max_fig=px.line(plot_df, x="arrival_day", y="rolling_p95", color="run")
max_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(max_fig.show())

max_fig=px.line(plot_df, x="arrival_day", y="rolling_dtas", color="run")
max_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(max_fig.show())

max_fig=px.line(plot_df, x="arrival_day", y="rolling_perf", color="run")
max_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(max_fig.show())

############################ Best flow scenario ###################################
print("Plots for best flow scenario")
#overwrite g class - so its easy to play around with
g.ed_inter_visit = (1440 / 25) # convert daily arrivals into inter-arrival time
g.sdec_inter_visit = (1440 / 0)
g.other_inter_visit = (1440 / 0)
g.number_of_nelbeds = 500
g.mean_time_in_bed = (150 * 60) # convert hrs to minutes
g.sd_time_in_bed = (347 * 60) # convert hrs to minutes
g.sim_duration = (240 * 24 * 60) # convert days into minutes
g.warm_up_period = (120 * 24 * 60)
g.number_of_runs = 5

# Call the run_trial method of our Trial object
all_event_logs, patient_df, patient_df_nowarmup, run_summary_df, trial_summary_df = Trial().run_trial()

df=patient_df

#add a column called arrival day
df["arrival_day"]=np.floor(df["arrival"]/1440)
#display(df)

#average q_time_hrs by day
plot_df=df.groupby(["arrival_day", "run"]).agg(
    q_time_hrs=("q_time_hrs", "mean"),
    med_hrs=("q_time_hrs", "median"),
    reneged=("renege", "count"),
    max_hrs=("q_time_hrs", "max"),
    p95_hrs=("q_time_hrs", lambda x: np.nanpercentile(x, 95)),
    dtas=("q_time_hrs", lambda x: (x > 12).sum()),
    perf=("q_time_hrs", lambda x: (x < 4).sum() / x.count() * 100)
).reset_index()

#display(plot_df)
#calculate rolling average by day
plot_df["rolling_qtime"]=(plot_df.groupby("run")["q_time_hrs"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_med"]=(plot_df.groupby("run")["med_hrs"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_reneged"]=(plot_df.groupby("run")["reneged"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_max"]=(plot_df.groupby("run")["max_hrs"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_p95"]=(plot_df.groupby("run")["p95_hrs"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_dtas"]=(plot_df.groupby("run")["dtas"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
plot_df["rolling_perf"]=(plot_df.groupby("run")["perf"]
                         .transform(lambda x: x.rolling(window=10, min_periods=1)
                                    .mean()))
#display(plot_df)

#plot mean q time
fig=px.line(plot_df, x="arrival_day", y="rolling_qtime", color="run")
fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(fig.show())

fig=px.line(plot_df, x="arrival_day", y="rolling_med", color="run")
fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(fig.show())

#plot daily reneged
r_fig=px.line(plot_df, x="arrival_day", y="rolling_reneged", color="run")
r_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(r_fig.show())

max_fig=px.line(plot_df, x="arrival_day", y="rolling_max", color="run")
max_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(max_fig.show())

max_fig=px.line(plot_df, x="arrival_day", y="rolling_p95", color="run")
max_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(max_fig.show())

max_fig=px.line(plot_df, x="arrival_day", y="rolling_dtas", color="run")
max_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(max_fig.show())

max_fig=px.line(plot_df, x="arrival_day", y="rolling_perf", color="run")
max_fig.add_vline(x=(g.warm_up_period / 60)/24, line_dash="dash")
display(max_fig.show())