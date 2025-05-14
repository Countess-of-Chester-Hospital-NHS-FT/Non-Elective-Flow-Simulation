import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from app.model import g, Trial

for i in range(25, 75, 5):

    daily_ed = i

    g.ed_inter_visit = (1440 / daily_ed) # convert daily arrivals into inter-arrival time
    g.sdec_inter_visit = (1440 / 11)
    g.other_inter_visit = (1440 / 3)
    g.number_of_nelbeds = 434
    g.mean_time_in_bed = (219 * 60) # convert hrs to minutes
    g.sd_time_in_bed = (347 * 60) # convert hrs to minutes
    g.sim_duration = (960 * 24 * 60) # convert days into minutes
    #g.warm_up_period = (120 * 24 * 60)
    g.number_of_runs = 10

    # Call the run_trial method of our Trial object
    all_event_logs, patient_df, patient_df_nowarmup, run_summary_df, trial_summary_df = Trial().run_trial()

    df=patient_df

    #add a column called arrival day
    df["arrival_day"]=np.floor(df["arrival"]/1440)
    #display(df)

    #average q_time_hrs by day
    plot_df=df.groupby(["arrival_day", "run"]).agg(
        q_time_hrs=("q_time_hrs", "mean")
    ).reset_index()

    #average q time overall
    plot_df2=df.groupby(["arrival_day"]).agg(
        q_time_hrs=("q_time_hrs", "mean")
    ).reset_index()

    plot_df2["rolling_qtime"]=(plot_df2["q_time_hrs"]
                            .transform(lambda x: x.rolling(window=60, min_periods=1)
                                        .mean()))

    #calculate rolling average by day
    plot_df["rolling_qtime"]=(plot_df.groupby("run")["q_time_hrs"]
                            .transform(lambda x: x.rolling(window=60, min_periods=1)
                                        .mean()))

    # Create figure
    fig = go.Figure()

    # Add individual run rolling mean traces
    for run in plot_df['run'].unique():
        run_data = plot_df[plot_df['run'] == run]
        fig.add_trace(go.Scatter(
            x=run_data['arrival_day'],
            y=run_data['rolling_qtime'],
            mode='lines',
            name=f'Run {run}',
            opacity=0.5  # Make individual lines slightly transparent
        ))

    # Add overall rolling mean trace in black
    fig.add_trace(go.Scatter(
        x=plot_df2['arrival_day'],
        y=plot_df2['rolling_qtime'],
        mode='lines',
        name='Overall Rolling Mean',
        line=dict(color='black', width=3)  # Make it stand out
    ))

    # Add vertical line for warm-up period
    fig.add_vline(x=(g.warm_up_period / 60) / 24, line_dash="dash")

    # Update layout for clarity
    fig.update_layout(
        title=f"Rolling Mean Queue Time by - ed admission demand: {daily_ed}",
        xaxis_title="Arrival Day",
        yaxis_title="Rolling Mean Queue Time (Hrs)",
        legend_title="Legend"
    )

    # Show figure
    display(fig.show())
