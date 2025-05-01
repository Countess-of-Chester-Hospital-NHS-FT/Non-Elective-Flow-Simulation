import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from app.model import g, Trial

# calculate los lists
# Fixed target mode
mode_target = 18 # example

# Try different sigma values (smaller sigma → thinner tails)
sigma_list = np.linspace(1.2, 1.34, 14)  # Adjust as you want

meanlos_list = []
std_list = []

for i, sigma in enumerate(sigma_list):
    # Adjust mu to keep mode constant
    mu = np.log(mode_target) + sigma**2

    # Calculate mean and std (in real space) if needed
    mean = np.exp(mu + 0.5 * sigma**2)
    std = np.sqrt((np.exp(sigma**2) - 1) * np.exp(2*mu + sigma**2))

    #add them to their list
    meanlos_list.append(mean)
    std_list.append(std)

# lists to loop over - adjust as required
#demand_list = list(range(36, 66, 2))
#sdec_list=[round(x * 0.5) for x in demand_list] #set to 0 for all demand through ED
#ed_list=[d - s for d, s in zip(demand_list, sdec_list)]
#check_list=[e + s for e, s in zip(ed_list, sdec_list)]

df = pd.DataFrame()

dtas_list = []
edadmissions_list = []
reneged_list = []
meanwait_list = []
discharge_list = []
sdecadmissions_list = []

for i in range(len(meanlos_list)):
        print(meanlos_list[i])

        #overwrite g class - so its easy to play around with
        g.ed_inter_visit = (1440 / 40)#(1440 / ed_list[i]) # convert daily arrivals into inter-arrival time
        g.sdec_inter_visit = 0 # (1440 / sdec_list[i]) # set to 0 for all demand through ED
        g.other_inter_visit = 0
        g.number_of_nelbeds = 456
        g.mean_time_in_bed = (meanlos_list[i] * 60) #(204 * 60) # convert hrs to minutes
        g.sd_time_in_bed = (std_list[i] * 60) #(355 * 60) # convert hrs to minutes
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
        value_discharges = trial_summary_df.loc['Total Discharges', 'Mean'] / (g.sim_duration / 60.0 / 24.0)
        value_sdecadmissions = trial_summary_df.loc['SDEC Admissions', 'Mean'] / (g.sim_duration / 60.0 / 24.0)
        dtas_list.append(value)
        edadmissions_list.append(value_admissions)
        reneged_list.append(value_reneged)
        meanwait_list.append(value_meanwait)
        discharge_list.append(value_discharges)
        sdecadmissions_list.append(value_sdecadmissions)

df['MeanLOS'] = meanlos_list
df['Daily DTAs'] = dtas_list
df['ED Admissions'] = edadmissions_list
df['Reneged'] = reneged_list
df['Mean DTA Wait'] = meanwait_list
df['Discharges'] = discharge_list
df['SDEC Admissions'] = sdecadmissions_list

### Multi value chart

#Reshape the DataFrame to long format
df_long = df.melt(id_vars='MeanLOS', 
                value_vars=['Daily DTAs', 'ED Admissions'],
                var_name='Metric', 
                value_name='Value')

# Filter and sort for 'Daily DTAs'
dta = df_long[df_long['Metric'] == 'Daily DTAs'].sort_values('MeanLOS').reset_index(drop=True)

# Find index where Value first exceeds 1
idx = dta[dta['Value'] > 1].index.min()

# Get Demand just before the threshold breach
first_demand = dta.loc[idx - 1, 'MeanLOS'] if idx and idx > 0 else None
# Create a single line chart with color based on the metric
fig = px.line(df_long, x='MeanLOS', y='Value', color='Metric', markers=True,
            line_dash='Metric',
            title='MeanLOS vs Multiple Metrics',
            labels={'Value': 'Value', 'MeanLOS': 'MeanLOS'})

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

###### Wait for admission chart
filtered_df = df[(df["Mean DTA Wait"] <= 900)]

fig = px.line(filtered_df, x = "MeanLOS", y = "Mean DTA Wait", markers=True,
              title='MeanLOS vs Mean ED Wait',
              labels={'Value': 'Value', 'MeanLOS': 'MeanLOS'})

fig.update_layout(template="plotly_white")

if first_demand is not None:
    fig.add_vline(
        x=first_demand,
        line_dash='dash',
        line_color='black',
        opacity=0.7
    )

fig.show()