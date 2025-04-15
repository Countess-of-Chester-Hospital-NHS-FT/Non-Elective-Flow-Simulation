import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from app.model import g, Trial

############################ default scenario ###################################
demand_list = list(range(30, 62, 2))

df = pd.DataFrame()

dtas_list = []
edadmissions_list = []
reneged_list = []
meanwait_list = []

for i in range(len(demand_list)):
    print(demand_list[i])

    #overwrite g class - so its easy to play around with
    g.ed_inter_visit = (1440 / demand_list[i]) # convert daily arrivals into inter-arrival time
    g.sdec_inter_visit = 0
    g.other_inter_visit = 0
    g.number_of_nelbeds = 430
    g.mean_time_in_bed = (219 * 60) # convert hrs to minutes
    g.sd_time_in_bed = (347 * 60) # convert hrs to minutes
    #g.sim_duration = (240 * 24 * 60) # convert days into minutes
    #g.warm_up_period = (300 * 24 * 60)
    g.number_of_runs = 10
    g.reneging = 0

    # Call the run_trial method of our Trial object
    all_event_logs, patient_df, patient_df_nowarmup, run_summary_df, trial_summary_df = Trial().run_trial()

    value = trial_summary_df.loc['12hr DTAs (per day)', 'Mean']
    value_admissions = trial_summary_df.loc['Admissions via ED', 'Mean'] / (g.sim_duration / 60.0 / 24.0)
    value_reneged = trial_summary_df.loc['Reneged', 'Mean'] / (g.sim_duration / 60.0 / 24.0)
    value_meanwait = trial_summary_df.loc['Mean Q Time (Hrs)', 'Mean']
    dtas_list.append(value)
    edadmissions_list.append(value_admissions)
    reneged_list.append(value_reneged)
    meanwait_list.append(value_meanwait)

df['Demand'] = demand_list
df['Daily DTAs'] = dtas_list
df['ED Admissions'] = edadmissions_list
df['Reneged'] = reneged_list
df['Mean DTA Wait'] = meanwait_list


####Plot############

### Melted chart

#Reshape the DataFrame to long format
df_long = df.melt(id_vars='Demand', 
                  value_vars=['Daily DTAs', 'ED Admissions', 'Mean DTA Wait'],
                  var_name='Metric', 
                  value_name='Value')

# Filter and sort for 'Daily DTAs'
dta = df_long[df_long['Metric'] == 'Daily DTAs'].sort_values('Demand').reset_index(drop=True)

# Find index where Value first exceeds 1
idx = dta[dta['Value'] > 1].index.min()

# Get Demand just before the threshold breach
first_demand = dta.loc[idx - 1, 'Demand'] if idx and idx > 0 else None

# Create a single line chart with color based on the metric
fig = px.line(df_long, x='Demand', y='Value', color='Metric', markers=True,
              line_dash='Metric',
              title='Demand vs Multiple Metrics',
              labels={'Value': 'Value', 'Demand': 'Demand'})

fig.update_layout(template='plotly_white')

#fig.update_traces(opacity=0.7)

# Step 3: Add vertical dashed line if condition met
if first_demand is not None:
    fig.add_vline(
        x=first_demand,
        line_dash='dash',
        line_color='black',
        opacity=0.7
        #annotation_text='Daily DTA > 1',
        #annotation_position='top left'
    )

fig.show()