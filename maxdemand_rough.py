import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from app.model import g, Trial

############################ default scenario ###################################
demand_list = list(range(30, 80, 5))

df = pd.DataFrame()

dtas_list = []
edadmissions_list = []
reneged_list = []

for i in range(len(demand_list)):
    print(i)
    print(demand_list[i])

    #overwrite g class - so its easy to play around with
    g.ed_inter_visit = (1440 / demand_list[i]) # convert daily arrivals into inter-arrival time
    g.sdec_inter_visit = 0
    g.other_inter_visit = 0
    g.number_of_nelbeds = 434
    g.mean_time_in_bed = (219 * 60) # convert hrs to minutes
    g.sd_time_in_bed = (347 * 60) # convert hrs to minutes
    g.sim_duration = (240 * 24 * 60) # convert days into minutes
    g.warm_up_period = (300 * 24 * 60)
    g.number_of_runs = 10

    # Call the run_trial method of our Trial object
    all_event_logs, patient_df, patient_df_nowarmup, run_summary_df, trial_summary_df = Trial().run_trial()

    value = trial_summary_df.loc['12hr DTAs (per day)', 'Mean']
    value_admissions = trial_summary_df.loc['Admissions via ED', 'Mean'] / (g.sim_duration / 60.0 / 24.0)
    value_reneged = trial_summary_df.loc['Reneged', 'Mean'] / (g.sim_duration / 60.0 / 24.0)
    dtas_list.append(value)
    edadmissions_list.append(value_admissions)
    reneged_list.append(value_reneged)

df['Demand'] = demand_list
df['Daily DTAs'] = dtas_list
df['ED Admissions'] = edadmissions_list
df['Reneged'] = reneged_list


####Plot############
fig = px.line(df, x='Demand', y='Daily DTAs', markers=True,
              title='Line Chart of Demand vs Daily 12 hr DTAs',
              labels={'Demand': 'Demand', 'Daily DTAs': 'Daily DTAs'})

fig.update_layout(template='plotly_white')

display(fig.show())

fig_admissions = px.line(df, x='Demand', y='ED Admissions', markers=True,
              title='Line Chart of Demand vs ED Admissions',
              labels={'Demand': 'Demand', 'ED Admissions': 'ED Admissions'})

fig_admissions.update_layout(template='plotly_white')

display(fig_admissions.show())

# fig_renege = px.line(df, x='Demand', y='Reneged', markers=True,
#               title='Line Chart of Demand vs Reneged',
#               labels={'Demand': 'Demand', 'Reneged': 'Reneged'})

# fig_renege.update_layout(template='plotly_white')

# display(fig_renege.show())

### Melted chart

#Reshape the DataFrame to long format
df_long = df.melt(id_vars='Demand', 
                  value_vars=['Daily DTAs', 'ED Admissions', 'Reneged'],
                  var_name='Metric', 
                  value_name='Value')

# Create a single line chart with color based on the metric
fig = px.line(df_long, x='Demand', y='Value', color='Metric', markers=True,
              title='Demand vs Multiple Metrics',
              labels={'Value': 'Count', 'Demand': 'Demand'})

fig.update_layout(template='plotly_white')

fig.show()