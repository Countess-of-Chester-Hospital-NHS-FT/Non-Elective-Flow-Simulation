import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import time
root_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.append(root_dir)
from app.model import g, Trial

def vary_demand(min_demand, max_demand, step, prop_sdec, beds, losi, runs,
                 escalation, reneging, prioritisation):
    
    start_time = time.time()
    print(f'function started {time.strftime("%H:%M:%S", time.gmtime(start_time))}')
    
    # set range of values for los
    mean_time_in_bed_list = [138.7382025354152,
    144.1204868652976,
    149.76134831621232,
    155.67473175398086,
    161.8754074290085,
    168.3790235999657,
    175.20216273322046,
    182.36240153482328,
    189.87837509120888,
    197.7698454156935,
    206.05777472038835,
    214.76440375750852,
    223.91333560032334,
    233.5296252623914,
    243.63987558436168,
    254.27233985074432,
    265.45703163483324,
    277.2258424086355,
    289.61266749646745,
    302.6535409960803]
    sd_time_in_bed_list = [248.9837009930806,
    262.9621106480747,
    277.822418063578,
    293.6256905003274,
    310.43755753899,
    328.3285748616339,
    347.3746187373278,
    367.6573139379976,
    389.26449806398347,
    412.2907255366589,
    436.83781482034146,
    463.0154427703993,
    490.9417903718149,
    520.7442445359864,
    552.5601610667529,
    586.5376943937254,
    622.8367002063923,
    661.6297177111919,
    703.1030388812503,
    747.4578727809351]
    # lists to loop over - adjust as required
    demand_list = list(range(min_demand, max_demand, step))
    sdec_list=[round(x * prop_sdec) for x in demand_list] #set to 0 for all demand through ED
    ed_list=[d - s for d, s in zip(demand_list, sdec_list)]
    check_list=[e + s for e, s in zip(ed_list, sdec_list)]

    df = pd.DataFrame()

    dtas_list = []
    edadmissions_list = []
    reneged_list = []
    meanwait_list = []
    discharge_list = []
    sdecadmissions_list = []
    los_12hr_list = []
    los_24hr_list = []
    los_48hr_list = []
    los_72hr_list = []


    for i in range(len(demand_list)):
        print(demand_list[i])

        #overwrite g class - so its easy to play around with
        g.ed_inter_visit = (1440 / ed_list[i]) # convert daily arrivals into inter-arrival time
        g.sdec_inter_visit = 0 if sdec_list[i] == 0 else (1440 / sdec_list[i]) # set to 0 for all demand through ED
        g.other_inter_visit = 0
        g.number_of_nelbeds = beds
        g.mean_time_in_bed = (mean_time_in_bed_list[losi] * 60) # convert hrs to minutes
        g.sd_time_in_bed = (sd_time_in_bed_list[losi] * 60) # convert hrs to minutes
        #g.sim_duration = (240 * 24 * 60) # convert days into minutes
        #g.warm_up_period = (300 * 24 * 60)
        g.number_of_runs = runs
        g.reneging = reneging
        g.escalation = escalation
        g.prioritisation = prioritisation

        # Call the run_trial method of our Trial object
        all_event_logs, patient_df, run_summary_df, trial_summary_df = Trial().run_trial()

        value = trial_summary_df.loc['12hr DTAs (per day)', 'Mean']
        value_admissions = trial_summary_df.loc['Admissions via ED', 'Mean'] / (g.sim_duration / 60.0 / 24.0)
        value_reneged = trial_summary_df.loc['Reneged (per day)', 'Mean']
        value_meanwait = trial_summary_df.loc['Mean Q Time (Hrs)', 'Mean']
        value_discharges = trial_summary_df.loc['Total Discharges', 'Mean'] / (g.sim_duration / 60.0 / 24.0)
        value_sdecadmissions = trial_summary_df.loc['SDEC Admissions', 'Mean'] / (g.sim_duration / 60.0 / 24.0)
        value_los_12hr = trial_summary_df.loc['12hr LoS Breaches (per day)', 'Mean']
        value_los_24hr = trial_summary_df.loc['24hr LoS Breaches (per day)', 'Mean']
        value_los_48hr = trial_summary_df.loc['48hr LoS Breaches (per day)', 'Mean']
        value_los_72hr = trial_summary_df.loc['72hr LoS Breaches (per day)', 'Mean']
        dtas_list.append(value)
        edadmissions_list.append(value_admissions)
        reneged_list.append(value_reneged)
        meanwait_list.append(value_meanwait)
        discharge_list.append(value_discharges)
        sdecadmissions_list.append(value_sdecadmissions)
        los_12hr_list.append(value_los_12hr)
        los_24hr_list.append(value_los_24hr)
        los_48hr_list.append(value_los_48hr)
        los_72hr_list.append(value_los_72hr)

    df['Demand'] = demand_list
    df['Daily DTAs'] = dtas_list
    df['ED Admissions'] = edadmissions_list
    df['Reneged (per day)'] = reneged_list
    df['Mean DTA Wait'] = meanwait_list
    df['Discharges'] = discharge_list
    df['SDEC Admissions'] = sdecadmissions_list
    df['Daily 12hr LoS Breaches'] = los_12hr_list
    df['Daily 24hr LoS Breaches'] = los_24hr_list
    df['Daily 48hr LoS Breaches'] = los_48hr_list
    df['Daily 72hr LoS Breaches'] = los_72hr_list

    #Specify metrics you want to show
    value_vars=['Daily DTAs', 
                                'ED Admissions', 
                                'SDEC Admissions',
                                'Daily 12hr LoS Breaches', 
                                #'Daily 24hr LoS Breaches',
                                #'Daily 48hr LoS Breaches', 
                                #'Daily 72hr LoS Breaches',
                                #'Reneged (per day)'
                                ]
    
    #Reshape the DataFrame to long format
    df_long = df.melt(id_vars='Demand', 
                    value_vars=value_vars,
                    var_name='Metric', 
                    value_name='Value')
    
    fig = px.line(df_long, x='Demand', y='Value', color='Metric', markers=True,
            line_dash='Metric',
            title='Demand vs Multiple Metrics',
            labels={'Value': 'Value', 'Demand': 'Demand'})

    fig.update_layout(template='plotly_white')


    stop_time = time.time()
    print(f'function stopped {time.strftime("%H:%M:%S", time.gmtime(stop_time))}')
    timer=stop_time-start_time
    print(f'timer: {time.strftime("%H:%M:%S", time.gmtime(timer))}')

    return df, fig, value_vars

# df, fig, value_vars = vary_demand(min_demand=36, max_demand=66, step=2, prop_sdec=0,
# beds=456, losi=10, runs=10, escalation=0, reneging=0, prioritisation=0)