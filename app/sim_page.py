import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from animation import animate

from model import g, Trial

st.set_page_config(
     layout="wide"
 )

#Initialise session state
if 'button_click_count' not in st.session_state:
  st.session_state.button_click_count = 0
if 'session_results' not in st.session_state:
    st.session_state['session_results'] = []
if 'session_inputs' not in st.session_state:
    st.session_state['session_inputs'] = []
if 'animation' not in st.session_state:
    st.session_state['animation'] = []

st.title("Non-Elective Flow Simulation")
st.header("(work in progress)")

with st.sidebar:
    mean_los_slider = st.slider("Adjust the mean los in hours",
                                min_value=175, max_value=275, value=219)
    sd_los_slider = st.slider("Adjust the los standard deviation",
                                min_value=300, max_value=450, value=347)
    num_nelbeds_slider = st.slider("Adjust the number of beds available",
                                min_value=380, max_value=500, value=434)
    daily_ed_adm_slider = st.slider("Adjust the average number of admissions via ED per day",
                                    min_value=25, max_value=55, value=39)
    daily_sdec_adm_slider = st.slider("Adjust the average number of admissions via SDEC per day",
                                    min_value=1, max_value=20, value=11)
    daily_other_adm_slider = st.slider("Adjust the average number of admissions via other routes per day",
                                    min_value=1, max_value=10, value=3)
    num_runs_slider = st. slider("Adjust the number of runs the model does",
                                 min_value=10, max_value=20, value=10)

g.mean_time_in_bed = (mean_los_slider * 60)
g.sd_time_in_bed = (sd_los_slider * 60)
g.number_of_nelbeds = num_nelbeds_slider
g.ed_inter_visit = 1440/daily_ed_adm_slider
g.sdec_inter_visit = 1440/daily_sdec_adm_slider #if daily_sdec_adm_slider != 0 else 0
g.other_inter_visit = 1440/daily_other_adm_slider #if daily_other_adm_slider != 0 else 0
g.number_of_runs = num_runs_slider

tab1, tab_animate, tab2 = st.tabs(["Run the model", "Animation", "Compare scenarios"])


with tab1:

    button_run_pressed = st.button("Run simulation")

    if button_run_pressed:
        with st.spinner("Simulating the system"):
            all_event_logs, patient_df, patient_df_nowarmup, run_summary_df, trial_summary_df = Trial().run_trial()
            
            # Adding to session state objects so we can compare scenarios
            #st.session_state['event_logs'] = all_event_logs
            
            # Comparing inputs
            st.session_state.button_click_count += 1
            col_name = f"Scenario {st.session_state.button_click_count}"
            # make dataframe with inputs, set an index, select as a series
            inputs_for_state = pd.DataFrame({
            'Input': ['Mean LoS', 'Number of beds', 'Admissions via ED', 
                'Admissions via SDEC', 'Admissions via Other', 'Number of runs'],
            col_name: [mean_los_slider, num_nelbeds_slider, daily_ed_adm_slider, 
                daily_sdec_adm_slider, daily_other_adm_slider, num_runs_slider]
            }).set_index('Input')[col_name]
            # Append input series to the session state
            st.session_state['session_inputs'].append(inputs_for_state)
            
            # Comparing results
            results_for_state = trial_summary_df['Mean']
            results_for_state.name = col_name
            st.session_state['session_results'].append(results_for_state)
        
            ################
            st.write(f"You've run {st.session_state.button_click_count} scenarios")
            st.write("These metrics are for a 60 day period")

            st.dataframe(trial_summary_df)
            ###################
            
            #filter dataset to ED
            ed_df_nowarmup = patient_df_nowarmup[patient_df_nowarmup["pathway"] == "ED"]

            #Create the histogram
            if ed_df_nowarmup['q_time_hrs'].mean() > 1 :
                fig = plt.figure(figsize=(8, 6))
                sns.histplot(
                ed_df_nowarmup['q_time_hrs'], 
                bins=range(int(ed_df_nowarmup['q_time_hrs'].min()), 
                        int(ed_df_nowarmup['q_time_hrs'].max()) + 1, 1), 
                kde=False)

                # # Set the boundary for the bins to start at 0
                plt.xlim(left=0)

                # Add vertical lines with labels
                lines = [
                    {"x": trial_summary_df.loc["Mean Q Time (Hrs)", "Mean"], "color": "tomato", "label": f'Mean Q Time: {round(trial_summary_df.loc["Mean Q Time (Hrs)", "Mean"])} hrs'},
                    {"x": 4, "color": "mediumturquoise", "label": f'4 Hr DTA Performance: {round(trial_summary_df.loc["Admitted 4hr DTA Performance (%)", "Mean"])}%'},
                    {"x": 12, "color": "royalblue", "label": f'12 Hr DTAs per day: {round(trial_summary_df.loc["12hr DTAs (per day)", "Mean"])}'},
                    {"x": trial_summary_df.loc["95th Percentile Q Time (Hrs)", "Mean"], "color": "goldenrod", "label": f'95th Percentile Q Time: {round(trial_summary_df.loc["95th Percentile Q Time (Hrs)", "Mean"])} hrs'},
                    {"x": trial_summary_df.loc["Max Q Time (Hrs)", "Mean"], "color": "slategrey", "label": f'Max Q Time: {round(trial_summary_df.loc["Max Q Time (Hrs)", "Mean"])} hrs'},
                ]

                for line in lines:
                    # Add the vertical line
                    plt.axvline(x=line["x"], color=line["color"], linestyle='--', linewidth=1, zorder=0)
                    
                    # Add label with text
                    plt.text(line["x"] + 2, plt.ylim()[1] * 0.95, line["label"], 
                            color=line["color"], ha='left', va='top', fontsize=10, rotation=90,
                            bbox=dict(facecolor='white', edgecolor='none', alpha=0.3, boxstyle='round,pad=0.5'))

                # Add transparent rectangles for confidence intervals
                ci_ranges = [
                    {"lower": trial_summary_df.loc["Mean Q Time (Hrs)", "Lower 95% CI"], 
                    "upper": trial_summary_df.loc["Mean Q Time (Hrs)", "Upper 95% CI"], "color": "tomato"},
                    {"lower": trial_summary_df.loc["95th Percentile Q Time (Hrs)", "Lower 95% CI"], 
                    "upper": trial_summary_df.loc["95th Percentile Q Time (Hrs)", "Upper 95% CI"], "color": "goldenrod"},
                    {"lower": trial_summary_df.loc["Max Q Time (Hrs)", "Lower 95% CI"], 
                    "upper": trial_summary_df.loc["Max Q Time (Hrs)", "Upper 95% CI"], "color": "slategrey"},
                ]

                for ci in ci_ranges:

                    plt.axvspan(
                        ci["lower"],
                        ci["upper"],
                        color=ci["color"],
                        alpha=0.2,
                        zorder=0)

                # Add labels and title if necessary
                plt.xlabel('Admission Delays (Hours)')
                plt.title('Histogram of Admission Delays (All Runs)')
                fig.text(0.8, 0.01, 'Boxes show 95% CI.', ha='center', fontsize=10)

                col1, col2, col3 = st.columns([3, 1, 1])  # Adjust column ratios
                with col1:  
                # Display the plot
                    st.pyplot(fig)
            else:
                st.write("Waiting times cannot be plotted on a histogram as there are no significant waits for admission")
            # ###################

with tab_animate:
    with st.spinner("Generating animation"):

        if 'all_event_logs' in globals():
            animation = animate(all_event_logs)

            st.session_state['animation'] = animation

        if st.session_state['animation']:
            st.markdown("""
                        Animation of a single run of the latest scenario.

                        If you are viewing on a small screen minimise the 
                        sidebar or download the plot.
                        """)
            st.plotly_chart(st.session_state['animation'],
                                    use_container_width=False,
                                    config = {'displayModeBar': False})
            
            st.download_button(
                    label="Download Plot as HTML",
                    data=st.session_state['animation'].to_html(full_html=False, include_plotlyjs="cdn"),
                    file_name="plot.html",
                    mime="text/html"
                )
            #st.dataframe(reshaped_logs)
        
with tab2:
    st.write(f"You've run {st.session_state.button_click_count} scenarios")

    # Convert series back to df, transpose, display
    if st.session_state.button_click_count > 0:
        st.write("Here are your inputs for each scenario")
        current_i_df = pd.DataFrame(st.session_state['session_inputs']).T
        st.dataframe(current_i_df)
        
        st.write("Here are your results for each scenario")
        current_state_df = pd.DataFrame(st.session_state['session_results']).T
        st.dataframe(current_state_df)