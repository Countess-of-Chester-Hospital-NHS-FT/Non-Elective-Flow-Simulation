import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from vidigi.prep import reshape_for_animations, generate_animation_df
from vidigi.animation import generate_animation
from vidigi.animation import animate_activity_log
from app.des_classes1 import g, Trial

#overwrite g class - so its easy to play around with
g.ed_inter_visit = (1440 / 38) # convert daily arrivals into inter-arrival time
g.sdec_inter_visit = (1440 / 11)
g.other_inter_visit = (1440 / 4)
g.number_of_nelbeds = 434
g.mean_time_in_bed = (225 * 60) # convert hrs to minutes
g.sd_time_in_bed = (405 * 60) # convert hrs to minutes
g.sim_duration = (60 * 24 * 60) # convert days into minutes
g.warm_up_period = (60 * 24 * 60)
g.number_of_runs = 10

# Call the run_trial method of our Trial object
all_event_logs, patient_df, patient_df_nowarmup, run_summary_df, trial_summary_df = Trial().run_trial()

#display(all_event_logs.head(1000))
display(all_event_logs.tail(1000))
#display(patient_df.tail(1000))
#display(run_summary_df.head(100))
#display(trial_summary_df.head(100))


###################DIAGNOSTIC PLOTS#############################

#####Number of beds occupied

# minutes = pd.Series(range(0, g.sim_duration + g.warm_up_period))

# run0_df = patient_df[patient_df['run'] == 0]
# beds = ((run0_df["admission_begins"].values[:, None] < minutes.values) &
#         ((run0_df["admission_complete"].values[:, None] > minutes.values) |
#          run0_df["admission_complete"].isna().values[:, None])).sum(axis=0)

# beds_df = pd.DataFrame({"minutes": minutes, "beds": beds})

# fig = px.line(beds_df, x = "minutes", y = "beds")

# fig.add_hline(y=434, line_dash="dash", line_color="lightblue",
#               opacity=0.5, 
#               annotation_text="max. beds", 
#               annotation_position="top left")

# fig.update_layout(template="plotly_dark")

# fig.show()

############ANIMATION#################################################

#print(all_event_logs['event_type'].unique())
filtered_logs = all_event_logs[all_event_logs['event_type'] != 'other']# & 
                               #(all_event_logs['time'] > 100000) &
                               #(all_event_logs['time'] < 102000)]

filtered_logs.head()

STEP_SNAPSHOT_MAX = g.number_of_nelbeds * 1.1 # ensure this exceeds number of beds
LIMIT_DURATION = g.sim_duration + g.warm_up_period
WRAP_QUEUES_AT = 15

reshaped_logs = reshape_for_animations(
    event_log=filtered_logs[filtered_logs['run']==0],
    every_x_time_units=30, # set to every hour as sim is in minutes
    step_snapshot_max=STEP_SNAPSHOT_MAX,
    limit_duration=LIMIT_DURATION,
    debug_mode=True
    )

reshaped_logs.head(15)

event_position_df = pd.DataFrame([
                    {'event': 'arrival',
                     'x':  50, 'y': 300,
                     'label': "Arrival" },

                     {'event': 'admission_wait_begins',
                     'x':  205, 'y': 75,
                     'label': "Waiting for Admission"},

                    {'event': 'sdec_admission_wait_begins',
                     'x':  205, 'y': 475,
                     'label': "Waiting for Admission"},

                     {'event': 'other_admission_wait_begins',
                     'x':  205, 'y': 700,
                     'label': "Waiting for Admission"},

                    {'event': 'admission_begins',
                     'x':  505, 'y': 75,
                     'resource':'number_of_nelbeds',
                     'label': "Admitted"},

                    {'event': 'exit',
                     'x':  670, 'y': 70,
                     'label': "Exit"}

                ])

def adapt_event(row):
        if "admission_wait_begins" in row["event"]:
                if row["pathway"] == "SDEC":
                        return "sdec_admission_wait_begins"
                elif row["pathway"] == "Other":
                        return "other_admission_wait_begins"
                else:
                        return row["event"]
        else:
                return row["event"]
            
reshaped_logs2 = reshaped_logs.assign(
            event=reshaped_logs.apply(adapt_event, axis=1)
            )

position_logs = generate_animation_df(full_patient_df=reshaped_logs2,
                                                 event_position_df=event_position_df,
                                                 wrap_queues_at=WRAP_QUEUES_AT,
                                                 step_snapshot_max=STEP_SNAPSHOT_MAX,
                                                 gap_between_entities=10, # need this and resource gap to be consistent
                                                 gap_between_resources=10, # if changing this, also need to specify in generate_animation 
                                                 gap_between_rows=30, # if changing this, also need to specify in generate_animation  
                                                 debug_mode=True
                                                 )

position_logs.sort_values(['patient', 'minute']).head(150)

filtered_position_logs = position_logs[(position_logs['minute'] > 120000) & (position_logs['minute'] < 150000)]

filtered_position_logs.sort_values(['patient', 'minute']).head(150)

def show_priority_icon(row):
        if "more" not in row["icon"]:
                if row["pathway"] == "SDEC":
                        return "🔴"
                elif row["pathway"] == "Other":
                        return "🟣"
                else:
                        return row["icon"]
        else:
                    return row["icon"]
            
filtered_position_logs2 = filtered_position_logs.assign(
            icon=filtered_position_logs.apply(show_priority_icon, axis=1)
            )

generate_animation(
        full_patient_df_plus_pos=filtered_position_logs2.sort_values(['patient', 'minute']),
        event_position_df= event_position_df,
        scenario=g(),
        debug_mode=True,
        setup_mode=False, # turns on and off gridlines
        include_play_button=True,
        icon_and_text_size= 16,
        plotly_height=800,
        frame_duration=600,
        frame_transition_duration=600,
        plotly_width=1500,
        override_x_max=600,
        override_y_max=900,
        #time_display_units="dhm",
        display_stage_labels=False,
        custom_resource_icon='⚬',
        add_background_image="img/sq8.png"
    )

###################HISTOGRAM###########################################################

#Convert wait times into hours
# all_results_patient_level['q_time_bed_hours'] = all_results_patient_level['Q Time Bed'] / 60.0
# all_results_patient_level['under4hrflag'] = np.where(all_results_patient_level['q_time_bed_hours'] < 4, 1, 0)
# all_results_patient_level['dta12hrflag'] = np.where(all_results_patient_level['q_time_bed_hours'] > 12, 1, 0)
# all_results_patient_level['q_time_bed_or_renege'] = all_results_patient_level['Q Time Bed|Renege'] / 60.0

# #Create the histogram
# fig = plt.figure(figsize=(8, 6))
# sns.histplot(
# all_results_patient_level['q_time_bed_hours'], 
# bins=range(int(all_results_patient_level['q_time_bed_hours'].min()), 
#         int(all_results_patient_level['q_time_bed_hours'].max()) + 1, 1), 
# kde=False)

# # # Set the boundary for the bins to start at 0
# plt.xlim(left=0)

# # Add vertical lines with labels
# lines = [
#     {"x": trial_summary.loc["Mean Q Time (Hrs)", "Mean"], "color": "tomato", "label": f'Mean Q Time: {round(trial_summary.loc["Mean Q Time (Hrs)", "Mean"])} hrs'},
#     {"x": 4, "color": "mediumturquoise", "label": f'4 Hr DTA Performance: {round(trial_summary.loc["4hr DTA Performance (%)", "Mean"])}%'},
#     {"x": 12, "color": "royalblue", "label": f'12 Hr DTAs per day: {round(trial_summary.loc["12hr DTAs", "Mean"])} hrs'},
#     {"x": trial_summary.loc["95th Percentile Q", "Mean"], "color": "goldenrod", "label": f'95th Percentile Q Time: {round(trial_summary.loc["95th Percentile Q", "Mean"])} hrs'},
#     {"x": trial_summary.loc["Max Q Time (Hrs)", "Mean"], "color": "slategrey", "label": f'Max Q Time: {round(trial_summary.loc["Max Q Time (Hrs)", "Mean"])} hrs'},
# ]

# for line in lines:
#     # Add the vertical line
#     plt.axvline(x=line["x"], color=line["color"], linestyle='--', linewidth=1, zorder=0)
    
#     # Add label with text
#     plt.text(line["x"] + 2, plt.ylim()[1] * 0.95, line["label"], 
#             color=line["color"], ha='left', va='top', fontsize=10, rotation=90,
#             bbox=dict(facecolor='white', edgecolor='none', alpha=0.3, boxstyle='round,pad=0.5'))

# # Add transparent rectangles for confidence intervals
# ci_ranges = [
#     {"lower": trial_summary.loc["Mean Q Time (Hrs)", "Lower 95% CI"], 
#     "upper": trial_summary.loc["Mean Q Time (Hrs)", "Upper 95% CI"], "color": "tomato"},
#     {"lower": trial_summary.loc["95th Percentile Q", "Lower 95% CI"], 
#     "upper": trial_summary.loc["95th Percentile Q", "Upper 95% CI"], "color": "goldenrod"},
#     {"lower": trial_summary.loc["Max Q Time (Hrs)", "Lower 95% CI"], 
#     "upper": trial_summary.loc["Max Q Time (Hrs)", "Upper 95% CI"], "color": "slategrey"},
# ]

# for ci in ci_ranges:

#     plt.axvspan(
#         ci["lower"],
#         ci["upper"],
#         color=ci["color"],
#         alpha=0.2,
#         zorder=0)

# # Add labels and title if necessary
# plt.xlabel('Admission Delays (Hours)')
# plt.title('Histogram of Admission Delays (All Runs)')
# fig.text(0.8, 0.01, 'Boxes show 95% CI.', ha='center', fontsize=10)
